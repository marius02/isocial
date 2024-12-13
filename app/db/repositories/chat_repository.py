import uuid

import openai
import tiktoken
import validators
from app.api.chat.models import ChatCreateResponse
from app.api.twitter.services import TwitterAPIService
from app.api.youtube.services import YouTubeAPIService
from app.db.models.chat import Chat
from app.db.models.responses import Response
from app.db.repositories.payments_repository import SubscriptionRepository
from fastapi import HTTPException
from sqlalchemy import desc
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload


class ChatRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    def count_tokens(self, comments: str, question: str = "", search: str = ""):
        encoding = tiktoken.encoding_for_model("gpt-3.5-turbo-1106")
        encoded_comments = encoding.encode(comments)[:2000]
        encoded_question = encoding.encode(question)[:2000]
        encoded_search = encoding.encode(search)[:2000]

        total_chat_tokens = sum(
            [len(encoded_comments), len(encoded_question), len(encoded_search)]
        )

        return {
            "decoded_comments": encoding.decode(encoded_comments),
            "decoded_question": encoding.decode(encoded_question),
            "decoded_search": encoding.decode(encoded_search),
            "total_tokens": total_chat_tokens,
        }

    def openai_get_completion(self, client: openai.Client, comments: str, prompt: str):
        messages = [
            {"role": "system", "content": "you are helpful assistant"},
            {
                "role": "user",
                "content": f"""The following are users comments about the content with each comment separated by a ;.
                                {prompt}
                                Comments: {comments}
                """,
            },
        ]

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo-1106",
                messages=messages,
                temperature=0,
            )
            return response.choices[0].message.content

        except openai.OpenAIError as e:
            raise HTTPException(status_code=500, detail=f"OpenAI Error: {str(e)}")

    async def create_chat(
        self, user_id: uuid.UUID, chat_data: dict, client: openai.Client
    ):
        youtube_service = YouTubeAPIService()
        comments = youtube_service.get_comments(chat_data.url)
        if isinstance(comments, dict):
            print("Invalid URL")
            raise HTTPException(detail=comments['detail'], status_code=400)
            

        counted_and_decoded_tokens = self.count_tokens(
            comments=comments, question=chat_data.question
        )

        # Get user token balance and check if the balance has enough tokens
        subscription_repo = SubscriptionRepository(self.db)
        balance = await subscription_repo.get_user_balance(user_id)

        if balance is None:
            raise HTTPException(status_code=404, detail="Balance not found for user")

        if balance >= counted_and_decoded_tokens.get("total_tokens"):
            new_chat = Chat(
                id=chat_data.chat_id,
                user_id=user_id,
                created_at=chat_data.created_at,
                platform=chat_data.platform,
                url=chat_data.url,
                commentblob=counted_and_decoded_tokens.get("decoded_comments"),
            )

            if chat_data.question:
                gpt_response = self.openai_get_completion(
                    client,
                    counted_and_decoded_tokens.get("decoded_comments"),
                    counted_and_decoded_tokens.get("decoded_question"),
                )

                new_response = Response(
                    question=counted_and_decoded_tokens.get("decoded_question"),
                    response=gpt_response,
                    tokens=counted_and_decoded_tokens.get("total_tokens"),
                    chat_id=new_chat.id,
                )

                try:
                    self.db.add(new_chat)
                    self.db.add(new_response)

                    await self.db.commit()
                    await self.db.refresh(new_chat)
                    await self.db.refresh(new_response)

                    # Deduct tokens from user's balance
                    await subscription_repo.decrease_user_balance(
                        user_id, counted_and_decoded_tokens.get("total_tokens")
                    )

                    return new_response

                except IntegrityError as e:
                    if "duplicate key value violates unique constraint" in str(e):
                        raise HTTPException(
                            status_code=400, detail="Chat with this ID already exists"
                        )
                    else:
                        raise HTTPException(
                            status_code=500, detail="Error while creating the chat"
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
        self, user_id: uuid.UUID, chat_data: dict, client: openai.Client
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
            counted_and_decoded_tokens = self.count_tokens(
                comments=tweets, question=chat_data.question, search=chat_data.search
            )
            # Get user token balance and check if the balance has enough tokens
            subscription_repo = SubscriptionRepository(self.db)
            balance = await subscription_repo.get_user_balance(user_id)

            if balance >= counted_and_decoded_tokens.get("total_tokens"):
                new_chat = Chat(
                    id=chat_data.chat_id,
                    user_id=user_id,
                    platform=chat_data.platform,
                    created_at=chat_data.date,
                    **{
                        f"img_url{i}": images_urls.get(f"img_url{i}")
                        for i in range(1, 5)
                    },
                    commentblob=counted_and_decoded_tokens.get("decoded_comments"),
                )

                gpt_response = ""

                if counted_and_decoded_tokens.get("decoded_question"):
                    gpt_response = self.openai_get_completion(
                        client,
                        counted_and_decoded_tokens.get("decoded_comments"),
                        counted_and_decoded_tokens.get("decoded_question"),
                    )

                new_response = Response(
                    question=counted_and_decoded_tokens.get("decoded_question"),
                    response=gpt_response
                    if gpt_response
                    else counted_and_decoded_tokens.get("decoded_comments"),
                    tokens=counted_and_decoded_tokens.get("total_tokens"),
                    chat_id=new_chat.id,
                )

                try:
                    self.db.add(new_chat)
                    self.db.add(new_response)

                    await self.db.commit()
                    await self.db.refresh(new_chat)
                    await self.db.refresh(new_response)

                    # deduct from user token balance
                    await subscription_repo.decrease_user_balance(
                        user_id, counted_and_decoded_tokens.get("total_tokens")
                    )

                    chat_with_response = ChatCreateResponse(
                        id=new_chat.id,
                        date=new_chat.created_at,
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

        counted_and_decoded_tokens = self.count_tokens(
            comments=chat.commentblob, question=chat_data.question
        )

        # Get user token balance and check if the balance has enough tokens
        subscription_repo = SubscriptionRepository(self.db)
        balance = await subscription_repo.get_user_balance(user_id)

        if balance >= counted_and_decoded_tokens.get("total_tokens"):
            gpt_response = self.openai_get_completion(
                client,
                counted_and_decoded_tokens.get("decoded_comments"),
                counted_and_decoded_tokens.get("decoded_question"),
            )

            new_response = Response(
                question=counted_and_decoded_tokens.get("decoded_question"),
                response=gpt_response
                if gpt_response
                else counted_and_decoded_tokens.get("decoded_comments"),
                tokens=counted_and_decoded_tokens.get("total_tokens"),
                chat_id=chat_data.chat_id,
            )

            try:
                self.db.add(new_response)

                await self.db.commit()
                await self.db.refresh(new_response)

                # deduct from user token balance
                await subscription_repo.decrease_user_balance(
                    user_id, counted_and_decoded_tokens.get("total_tokens")
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

        counted_and_decoded_tokens = self.count_tokens(
            chat.commentblob, question=chat_data.question
        )

        # Get user token balance and check if the balance has enough tokens
        subscription_repo = SubscriptionRepository(self.db)
        balance = await subscription_repo.get_user_balance(user_id)

        if balance >= counted_and_decoded_tokens.get("total_tokens"):
            gpt_response = self.openai_get_completion(
                client,
                counted_and_decoded_tokens.get("decoded_comments"),
                counted_and_decoded_tokens.get("decoded_question"),
            )

            new_response = Response(
                question=counted_and_decoded_tokens.get("decoded_question"),
                response=gpt_response,
                tokens=counted_and_decoded_tokens.get("total_tokens"),
                chat_id=chat_data.chat_id,
            )
            try:
                self.db.add(new_response)

                await self.db.commit()
                await self.db.refresh(new_response)

                # deduct from user token balance
                await subscription_repo.decrease_user_balance(
                    user_id, counted_and_decoded_tokens.get("total_tokens")
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
