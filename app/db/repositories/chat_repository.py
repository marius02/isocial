import uuid

import openai
import validators
from app.api.chat.models import ChatCreateResponse
from app.api.twitter.services import TwitterAPIService
from app.api.youtube.services import YouTubeAPIService
from app.db.models.chat import Chat
from app.db.models.responses import Response
from app.db.repositories.payments_repository import SubscriptionRepository
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import desc
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload


class ChatRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    def count_tokens(self, comments: str, question: str, search: str = ""):
        input_total_tokens = 0

        # TODO: REPLACE LEN WITH OPENAI TIKTOKEN TO COUNT TOKENS CORRECTLY
        if comments:
            if len(comments) <= 2000:
                input_total_tokens += len(comments)
            else:
                input_total_tokens += 2000
        else:
            input_total_tokens += 0

        if question:
            if len(question) <= 2000:
                input_total_tokens += len(question)
            else:
                input_total_tokens += 2000
        else:
            input_total_tokens += 0

        if search:
            search_tokens = len(search)

            total_chat_tokens = (
                (4097 - int(input_total_tokens) - int(search_tokens))
                + int(input_total_tokens)
                + int(search_tokens)
            )
            if comments and question:
                return comments[:2000], question[:2000], search, total_chat_tokens
            else:
                return "", "", search, total_chat_tokens
        else:
            total_chat_tokens = (4097 - int(input_total_tokens)) + int(
                input_total_tokens
            )

            if comments and question:
                return comments[:2000], question[:2000], search, total_chat_tokens
            else:
                return "", "", search, total_chat_tokens

    async def openai_get_completion(
        self, client: openai.AsyncClient, comments: str, prompt: str
    ):
        messages = [
            {
                "role": "user",
                "content": f"""The following are users comments about the content with each comment separated by a ;.
                                {prompt}
                                Comments: {comments}
                """,
            }
        ]

        try:
            response = await client.chat.completions.create(
                model="gpt-3.5-turbo-1106",
                messages=messages,
                temperature=0,
                stream=True,
            )
            return response

        except openai.OpenAIError as e:
            raise HTTPException(status_code=500, detail=f"OpenAI Error: {str(e)}")

    async def create_chat(
        self, user_id: uuid.UUID, chat_data: dict, client: openai.AsyncClient
    ):
        youtube_service = YouTubeAPIService()
        comments = youtube_service.get_comments(chat_data.url)

        if isinstance(comments, dict):
            yield JSONResponse(content=comments, status_code=400)

        decoded_comments, decoded_question, _, total_chat_tokens = self.count_tokens(
            comments, chat_data.question
        )

        # Get user token balance and check if the balance has enough tokens
        subscription_repo = SubscriptionRepository(self.db)
        balance = await subscription_repo.get_user_balance(user_id)

        if balance >= total_chat_tokens:
            new_chat = Chat(
                id=chat_data.chat_id,
                user_id=user_id,
                platform=chat_data.platform,
                url=chat_data.url,
                commentblob=decoded_comments,
            )

            if chat_data.question:
                gpt_response = await self.openai_get_completion(
                    client, decoded_comments, decoded_question
                )
                content = ""
                async for chunk in gpt_response:
                    if chunk.choices[0].delta.content:
                        content += chunk.choices[0].delta.content
                        yield chunk.choices[0].delta.content

                new_response = Response(
                    question=decoded_question,
                    response=content,
                    tokens=total_chat_tokens,
                    chat_id=new_chat.id,
                )

                try:
                    self.db.add(new_chat)
                    self.db.add(new_response)

                    await self.db.commit()
                    await self.db.refresh(new_chat)
                    await self.db.refresh(new_response)

                    # deduct from user token balance
                    subscription = await subscription_repo.decrease_user_balance(
                        user_id, total_chat_tokens
                    )

                except IntegrityError as e:
                    if "duplicate key value violates unique constraint" in str(e):
                        raise HTTPException(
                            status_code=400, detail="Chat with this ID already exists"
                        )
                    else:
                        raise HTTPException(
                            status_code=500,
                            detail="An error occurred while creating the chat",
                        )

        else:
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "INSUFFICIENT_BALANCE",
                    "reason": "Not enough balance, please purchase more tokens",
                },
            )

    async def create_search(
        self, user_id: uuid.UUID, chat_data: dict, client: openai.AsyncClient
    ):
        # Check if the search term has more than 2 words
        if len(chat_data.search.split()) > 2:
            raise HTTPException(
                status_code=400,
                detail={
                    "token_type": "bearer",
                    "code": "INVALID_SEARCH",
                    "reason": "Max two words are expected",
                },
            )

        # Check if the search term is a URL
        elif validators.url(chat_data.search):
            raise HTTPException(
                status_code=400,
                detail={
                    "token_type": "bearer",
                    "code": "INVALID_SEARCH",
                    "reason": "Only search terms expected",
                },
            )

        else:
            twitter_service = TwitterAPIService()
            tweets, images_urls = twitter_service.get_tweets(chat_data.search)
            decoded_tweets, decoded_question, decoded_search, total_chat_tokens = (
                self.count_tokens(tweets, chat_data.search, chat_data.question)
            )

            # Get user token balance and check if the balance has enough tokens
            subscription_repo = SubscriptionRepository(self.db)
            balance = await subscription_repo.get_user_balance(user_id)

            if balance >= total_chat_tokens:
                new_chat = Chat(
                    id=chat_data.chat_id,
                    user_id=user_id,
                    platform=chat_data.platform,
                    created_at=chat_data.date,
                    **{
                        f"img_url{i}": images_urls.get(f"img_url{i}")
                        for i in range(1, 5)
                    },
                    commentblob=decoded_tweets,
                )

                content = ""

                if decoded_question:
                    gpt_response = await self.openai_get_completion(
                        client, decoded_tweets, decoded_question
                    )
                    content = ""
                    async for chunk in gpt_response:
                        if chunk.choices[0].delta.content:
                            content += chunk.choices[0].delta.content

                new_response = Response(
                    search=decoded_search,
                    question=decoded_question,
                    response=content if content else decoded_tweets,
                    tokens=total_chat_tokens,
                    chat_id=new_chat.id,
                )

                try:
                    self.db.add(new_chat)
                    self.db.add(new_response)

                    await self.db.commit()
                    await self.db.refresh(new_chat)
                    await self.db.refresh(new_response)

                    # deduct from user token balance
                    subscription = await subscription_repo.decrease_user_balance(
                        user_id, total_chat_tokens
                    )

                    # new_chat.created_at = new_chat.created_at.strftime(
                    #     "%Y-%m-%d")
                    chat_with_response = ChatCreateResponse(
                        id=new_chat.id,
                        created_at=new_chat.created_at,
                        platform=new_chat.platform,
                        img_url1=new_chat.img_url1,
                        img_url2=new_chat.img_url2,
                        img_url3=new_chat.img_url3,
                        img_url4=new_chat.img_url4,
                        response=new_response.response,
                    )
                    return chat_with_response

                except IntegrityError as e:
                    if "duplicate key value violates unique constraint" in str(e):
                        raise HTTPException(
                            status_code=400,
                            detail="Chat with this ID already exists",
                        )
                    else:
                        raise HTTPException(
                            status_code=500,
                            detail="An error occurred while creating the chat",
                        )

            else:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "code": "INSUFFICIENT_BALANCE",
                        "reason": "Not enough balance, please purchase more tokens",
                    },
                )

    async def continue_chat(self, user_id: uuid.UUID, client, chat_data: dict):
        stmt = select(Chat).where(
            (Chat.id == chat_data.chat_id)
            & (Chat.user_id == user_id)
            & (Chat.delete == "N")
        )
        result = await self.db.execute(stmt)

        chat = result.scalar()

        if not chat:
            raise HTTPException(
                status_code=404, detail=f"Chat with id:{chat_data.chat_id} not found"
            )

        decoded_comments, decoded_question, _, total_chat_tokens = self.count_tokens(
            chat.commentblob, chat_data.question
        )

        # Get user token balance and check if the balance has enough tokens
        subscription_repo = SubscriptionRepository(self.db)
        balance = await subscription_repo.get_user_balance(user_id)

        if balance >= total_chat_tokens:
            gpt_response = await self.openai_get_completion(
                client, decoded_comments, decoded_question
            )

            content = ""
            async for chunk in gpt_response:
                if chunk.choices[0].delta.content:
                    content += chunk.choices[0].delta.content

            new_response = Response(
                question=decoded_question,
                response=content,
                tokens=total_chat_tokens,
                chat_id=chat_data.chat_id,
            )
            try:
                self.db.add(new_response)

                await self.db.commit()
                await self.db.refresh(new_response)

                # deduct from user token balance
                subscription = await subscription_repo.decrease_user_balance(
                    user_id, total_chat_tokens
                )

                return new_response

            except IntegrityError as e:
                if "duplicate key value violates unique constraint" in str(e):
                    raise HTTPException(
                        status_code=400, detail="Chat with this ID already exists"
                    )
                else:
                    raise HTTPException(
                        status_code=500,
                        detail="An error occurred while creating the chat",
                    )

        else:
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "INSUFFICIENT_BALANCE",
                    "reason": "Not enough balance, please purchase more tokens",
                },
            )

    async def continue_search(self, user_id: uuid.UUID, client, chat_data: dict):
        stmt = select(Chat).where(
            (Chat.id == chat_data.chat_id)
            & (Chat.user_id == user_id)
            & (Chat.delete == "N")
        )
        result = await self.db.execute(stmt)

        chat = result.scalar()

        if not chat:
            raise HTTPException(
                status_code=404, detail=f"Chat with id:{chat_data.chat_id} not found"
            )

        decoded_tweets, decoded_question, _, total_chat_tokens = self.count_tokens(
            chat.commentblob, chat_data.question
        )

        # Get user token balance and check if the balance has enough tokens
        subscription_repo = SubscriptionRepository(self.db)
        balance = await subscription_repo.get_user_balance(user_id)

        if balance >= total_chat_tokens:
            gpt_response = await self.openai_get_completion(
                client, decoded_tweets, decoded_question
            )

            content = ""
            async for chunk in gpt_response:
                if chunk.choices[0].delta.content:
                    content += chunk.choices[0].delta.content

            new_response = Response(
                question=decoded_question,
                response=content,
                tokens=total_chat_tokens,
                date=chat_data.date,
                chat_id=chat_data.chat_id,
            )
            try:
                self.db.add(new_response)

                await self.db.commit()
                await self.db.refresh(new_response)

                # deduct from user token balance
                subscription = await subscription_repo.decrease_user_balance(
                    user_id, total_chat_tokens
                )

                return new_response

            except IntegrityError as e:
                if "duplicate key value violates unique constraint" in str(e):
                    raise HTTPException(
                        status_code=400, detail="Chat with this ID already exists"
                    )
                else:
                    raise HTTPException(
                        status_code=500,
                        detail="An error occurred while creating the chat",
                    )

        else:
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "INSUFFICIENT_BALANCE",
                    "reason": "Not enough balance, please purchase more tokens",
                },
            )

    async def delete_chat(self, user_id: uuid.UUID, chat_id: uuid.UUID):
        stmt = select(Chat).where((Chat.id == chat_id) & (Chat.user_id == user_id))
        result = await self.db.execute(stmt)
        chat = result.scalar()

        if chat:
            chat.delete = "Y"
            await self.db.commit()
            return {"detail": {"code": "DELETE_SUCCESSFUL", "reason": "Chat deleted"}}
        else:
            raise HTTPException(status_code=404, detail="Chat not found")

    async def get_chat(self, user_id: uuid.UUID, chat_id: uuid.UUID):
        stmt = (
            select(Chat)
            .where(
                (Chat.id == chat_id) & (Chat.user_id == user_id) & (Chat.delete == "N")
            )
            .options(selectinload(Chat.chats))
        )
        result = await self.db.execute(stmt)
        chat = result.scalar()

        if chat:
            return chat
        else:
            raise HTTPException(
                status_code=404, detail=f"Chat with id:{chat_id} not found"
            )

    async def get_user_chats(self, user_id):
        stmt = (
            select(Chat)
            .where((Chat.user_id == user_id) & (Chat.delete == "N"))
            .order_by(desc(Chat.created_at))
        )
        result = await self.db.execute(stmt)
        chats = result.scalars().all()

        return {"chats": chats}
