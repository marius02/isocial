import uuid
from api.chat.models import ChatCreate
from db.db_config import get_async_session
from db.repositories.chat_repository import ChatRepository
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from api.users.services import current_active_user

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.get("/user_chats/")
async def get_user_chats(user=Depends(current_active_user), db: AsyncSession = Depends(get_async_session)):
    chat_repo = ChatRepository(db)
    return await chat_repo.get_user_chats(user.id)


@router.post("/")
async def create_chat(user=Depends(current_active_user), db: AsyncSession = Depends(get_async_session)):
    chat_repo = ChatRepository(db)
    return await chat_repo.create_chat(user.id)


@router.delete("/{chat_id}/")
async def delete_chat(chat_id: uuid.UUID, user=Depends(current_active_user),  db: AsyncSession = Depends(get_async_session)):
    chat_repo = ChatRepository(db)
    return await chat_repo.delete_chat(user.id, chat_id)


@router.get("/{chat_id}/")
async def get_chat(chat_id: uuid.UUID, user=Depends(current_active_user), db: AsyncSession = Depends(get_async_session)):
    chat_repo = ChatRepository(db)
    return await chat_repo.get_chat(user.id, chat_id)
