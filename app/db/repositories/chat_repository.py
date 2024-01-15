from fastapi import HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import desc
from app.db.models.chat import Chat
from app.db.models.responses import Response
from app.db.repositories.payments_repository import SubscriptionRepository
from app.api.youtube.services import YouTubeAPIService
import uuid
import openai


class ChatRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    def count_tokens(self, comments: str, question: str):

        input_total_tokens = 0

        if len(comments) <= 2000:
            input_total_tokens += len(comments)
        else:
            input_total_tokens += 2000

        if len(question) <= 2000:
            input_total_tokens += len(question)
        else:
            input_total_tokens += 2000

        total_chat_tokens = (4097 - int(input_total_tokens)
                             ) + int(input_total_tokens)

        return comments[:2000], question[:2000], total_chat_tokens

    async def openai_get_completion(self, client: openai.AsyncClient, comments: str, prompt: str):
        messages = [
            {
                "role": "user",
                "content": f"""The following are users comments about the content with each comment separated by a ;.
                                {prompt}
                                Comments: {comments}
                """
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
            raise HTTPException(
                status_code=500, detail=f"OpenAI Error: {str(e)}")

    async def create_chat(self, user_id: uuid.UUID, chat_data: dict, client: openai.AsyncClient):
        youtube_service = YouTubeAPIService()
        comments = youtube_service.get_comments(chat_data.url)

        if isinstance(comments, dict):
            yield JSONResponse(content=comments, status_code=400)

        decoded_comments, decoded_question, total_chat_tokens = self.count_tokens(comments,
                                                                                  chat_data.question)

        # Get user token balance and check if the balance has enough tokens
        subscription_repo = SubscriptionRepository(self.db)
        balance = await subscription_repo.get_user_balance(user_id)

        if balance >= total_chat_tokens:
            new_chat = Chat(id=chat_data.chat_id,
                            user_id=user_id,
                            platform=chat_data.platform,
                            url=chat_data.url,
                            commentblob=decoded_comments)

            if chat_data.question:
                gpt_response = await self.openai_get_completion(client, decoded_comments, decoded_question)
                content = ""
                async for chunk in gpt_response:
                    if chunk.choices[0].delta.content:
                        content += chunk.choices[0].delta.content
                        yield chunk.choices[0].delta.content

                new_response = Response(
                    question=decoded_question, response=content, tokens=total_chat_tokens, chat_id=new_chat.id)

            try:
                self.db.add(new_chat)
                self.db.add(new_response)

                await self.db.commit()
                await self.db.refresh(new_chat)
                await self.db.refresh(new_response)

                # deduct from user token balance
                subscription = await subscription_repo.decrease_user_balance(
                    user_id, total_chat_tokens)

            except IntegrityError as e:
                if "duplicate key value violates unique constraint" in str(e):
                    raise HTTPException(
                        status_code=400, detail="Chat with this ID already exists")
                else:
                    raise HTTPException(
                        status_code=500, detail="An error occurred while creating the chat")

        else:
            raise HTTPException(
                status_code=400, detail={"code": "INSUFFICIENT_BALANCE",
                                         "reason": "Not enough balance, please purchase more tokens"}
            )

    async def continue_chat(self, user_id: uuid.UUID, client, chat_data: dict):
        stmt = select(Chat).where(
            (Chat.id == chat_data.chat_id) & (Chat.user_id == user_id) & (Chat.delete == "N"))
        result = await self.db.execute(stmt)

        chat = result.scalar()

        if not chat:
            raise HTTPException(
                status_code=404, detail=f"Chat with id:{chat_data.chat_id} not found")

        decoded_comments, decoded_question, total_chat_tokens = self.count_tokens(chat.commentblob,
                                                                                  chat_data.question)

        # Get user token balance and check if the balance has enough tokens
        subscription_repo = SubscriptionRepository(self.db)
        balance = await subscription_repo.get_user_balance(user_id)

        if balance >= total_chat_tokens:
            gpt_response = await self.openai_get_completion(client, decoded_comments, decoded_question)

            content = ""
            async for chunk in gpt_response:
                if chunk.choices[0].delta.content:
                    content += chunk.choices[0].delta.content
                    yield chunk.choices[0].delta.content

            new_response = Response(question=decoded_question,
                                    response=content,
                                    tokens=total_chat_tokens,
                                    chat_id=chat_data.chat_id)
            try:
                self.db.add(new_response)

                await self.db.commit()
                await self.db.refresh(new_response)

                # deduct from user token balance
                subscription = await subscription_repo.decrease_user_balance(user_id, total_chat_tokens)

            except IntegrityError as e:
                if "duplicate key value violates unique constraint" in str(e):
                    raise HTTPException(
                        status_code=400, detail="Chat with this ID already exists")
                else:
                    raise HTTPException(
                        status_code=500, detail="An error occurred while creating the chat")

        else:
            raise HTTPException(
                status_code=400, detail={"code": "INSUFFICIENT_BALANCE",
                                         "reason": "Not enough balance, please purchase more tokens"}
            )

    async def delete_chat(self, user_id: uuid.UUID, chat_id: uuid.UUID):
        stmt = select(Chat).where(
            (Chat.id == chat_id) & (Chat.user_id == user_id)
        )
        result = await self.db.execute(stmt)
        chat = result.scalar()

        if chat:
            chat.delete = "Y"
            await self.db.commit()
            return {"detail": {"code": "DELETE_SUCCESSFUL", "reason": "Chat deleted"}}
        else:
            raise HTTPException(
                status_code=404, detail=f"Chat not found")

    async def get_chat(self, user_id: uuid.UUID, chat_id: uuid.UUID):
        stmt = select(Chat).where(
            (Chat.id == chat_id) & (Chat.user_id == user_id) & (Chat.delete == "N")).options(selectinload(Chat.chats))
        result = await self.db.execute(stmt)
        chat = result.scalar()

        if chat:
            return chat
        else:
            raise HTTPException(
                status_code=404, detail=f"Chat with id:{chat_id} not found")

    async def get_user_chats(self, user_id):
        stmt = select(Chat).where(
            (Chat.user_id == user_id) & (Chat.delete == "N")
        ).order_by(desc(Chat.created_at))
        result = await self.db.execute(stmt)
        chats = result.scalars().all()

        return {"chats": chats}
