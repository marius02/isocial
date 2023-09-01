from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from db.models.chat import Chat
from db.models.responses import Response
from api.youtube.services import YouTubeAPIService
from api.openai.services import OpenAIService
import uuid


class ChatRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_chat(self, user_id: uuid.UUID, chat_data: dict):
        youtube_service = YouTubeAPIService()
        comments: list = youtube_service.get_comments(chat_data.url)
        new_chat = Chat(id=chat_data.chat_id,
                        user_id=user_id,
                        url=chat_data.url,
                        commentblob=comments)

        if chat_data.question:
            openai_service = OpenAIService()
            gpt_response = openai_service.get_completion(
                comments, chat_data.question)

            new_response = Response(
                question=chat_data.question, response=gpt_response, chat_id=new_chat.id)

        try:
            self.db.add(new_chat)
            self.db.add(new_response)

            await self.db.commit()
            await self.db.refresh(new_chat)
            await self.db.refresh(new_response)

            return new_response

        except IntegrityError as e:
            if "duplicate key value violates unique constraint" in str(e):
                raise HTTPException(
                    status_code=400, detail="Chat with this ID already exists")
            else:
                raise HTTPException(
                    status_code=500, detail="An error occurred while creating the chat")

    async def continue_chat(self, user_id: uuid.UUID, chat_data: dict):
        stmt = select(Chat).where(
            (Chat.id == chat_data.chat_id) & (Chat.user_id == user_id))
        result = await self.db.execute(stmt)

        chat = result.scalar()

        if chat:
            openai_service = OpenAIService()
            gpt_response = openai_service.get_completion(
                chat.commentblob, chat_data.question)

            new_response = Response(question=chat_data.question,
                                    response=gpt_response,
                                    chat_id=chat_data.chat_id)
            try:
                self.db.add(new_response)

                await self.db.commit()
                await self.db.refresh(new_response)
                return new_response

            except IntegrityError as e:
                if "duplicate key value violates unique constraint" in str(e):
                    raise HTTPException(
                        status_code=400, detail="Chat with this ID already exists")
                else:
                    raise HTTPException(
                        status_code=500, detail="An error occurred while creating the chat")
        else:
            raise HTTPException(
                status_code=404, detail=f"Chat with id:{chat_data.chat_id} not found")

    async def delete_chat(self, user_id: uuid.UUID, chat_id: uuid.UUID):
        stmt = select(Chat).where(
            (Chat.id == chat_id) & (Chat.user_id == user_id)
        )
        result = await self.db.execute(stmt)
        chat = result.scalar()

        if chat:
            await self.db.delete(chat)
            await self.db.commit()
            return {"message": f"Chat with id:{chat_id} has successfully deleted"}
        else:
            raise HTTPException(
                status_code=404, detail=f"Chat with id:{chat_id} not found")

    async def get_chat(self, user_id: uuid.UUID, chat_id: uuid.UUID):
        stmt = select(Chat).where(
            (Chat.id == chat_id) & (Chat.user_id == user_id)
        ).options(selectinload(Chat.chats))
        result = await self.db.execute(stmt)
        chat = result.scalar()

        if chat:
            return chat
        else:
            raise HTTPException(
                status_code=404, detail=f"Chat with id:{chat_id} not found")

    async def get_user_chats(self, user_id):
        stmt = select(Chat).where(Chat.user_id == user_id)
        result = await self.db.execute(stmt)
        chats = result.scalars().all()

        return {"chats": chats}
