from sqlalchemy.ext.asyncio import AsyncSession
from db.models.chat import Chat


class ChatRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_chat(self):
        chat = Chat()
        self.db.add(chat)

        await self.db.commit()
        await self.db.refresh(chat)
        return chat

    async def delete_chat(self, chat: Chat):
        self.db.delete(chat)
        await self.db.commit()

    async def get_chat(self, chat_id: int):
        return await self.db.query(Chat).filter(Chat.id == chat_id).first()
