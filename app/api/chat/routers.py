from api.chat.models import ChatCreate
from db.db_config import get_async_session
from db.repositories.chat_repository import ChatRepository
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/", response_model=ChatCreate)
async def create_chat(db: AsyncSession = Depends(get_async_session)):
    chat_repo = ChatRepository(db)
    return await chat_repo.create_chat()


@router.delete("/{chat_id}/")
async def delete_chat(chat_id: int, db: AsyncSession = Depends(get_async_session)):
    chat_repo = ChatRepository(db)
    chat = await chat_repo.get_chat(chat_id)
    if chat:
        await chat_repo.delete_chat(chat)
        return {"message": "Chat deleted"}
    return {"message": "Chat not found"}


@router.get("/{chat_id}/", response_model=ChatCreate)
async def get_chat(chat_id: int, db: AsyncSession = Depends(get_async_session)):
    chat_repo = ChatRepository(db)
    chat = await chat_repo.get_chat(chat_id)
    if chat:
        return chat
    return {"message": "Chat not found"}
