from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from db.models.chat import Chat
import uuid


class ChatRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_chat(self, user_id: uuid.UUID):
        chat = Chat(user_id=user_id)
        self.db.add(chat)

        await self.db.commit()
        await self.db.refresh(chat)
        return chat

    async def delete_chat(self, user_id: uuid.UUID, chat_id: uuid.UUID):
        stmt = select(Chat).where(
            (Chat.id == chat_id) & (Chat.user_id == user_id)
        )
        result = await self.db.execute(stmt)
        chat = result.scalar()

        if chat:
            await self.db.delete(chat)
            await self.db.commit()
            return {"message": "Chat deleted"}
        else:
            raise HTTPException(status_code=404, detail="Chat not found")

    async def get_chat(self, user_id: uuid.UUID, chat_id: uuid.UUID):
        stmt = select(Chat).where(
            (Chat.id == chat_id) & (Chat.user_id == user_id)
        )
        result = await self.db.execute(stmt)
        chat = result.scalar()

        if chat:
            return chat
        else:
            raise HTTPException(status_code=404, detail="Chat not found")

    async def get_user_chats(self, user_id):
        stmt = select(Chat).where(Chat.user_id == user_id)
        result = await self.db.execute(stmt)
        chats = result.scalars().all()

        return chats
