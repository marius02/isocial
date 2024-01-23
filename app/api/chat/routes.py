import uuid

from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager
from app.api.chat.models import (Chat,
                                 AllChats,
                                 YouTubeChatData,
                                 TwitterChatData,
                                 ChatContinueData,
                                 ChatContinueResponse,
                                 ChatCreateResponse)
from app.db.db_config import get_async_session
from app.db.repositories.chat_repository import ChatRepository
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.users.services import current_active_user
import openai
import os
from dotenv import load_dotenv

load_dotenv()


def init_openai_client():
    client = openai.AsyncOpenAI()
    client.api_key = os.getenv("OPENAI_API_KEY")
    return client


initial_dependencies = {}


@asynccontextmanager
async def lifespan(app: APIRouter):
    initial_dependencies["openai_client"] = init_openai_client()
    yield
    initial_dependencies.clear()

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.get("/list", response_model=AllChats)
async def get_user_chats(user=Depends(current_active_user), db: AsyncSession = Depends(get_async_session)):
    chat_repo = ChatRepository(db)
    return await chat_repo.get_user_chats(user.id)


@router.post("/", response_model=ChatCreateResponse)
async def create_new_chat(chat_data: YouTubeChatData, user=Depends(current_active_user), db: AsyncSession = Depends(get_async_session), client=Depends(init_openai_client)):
    chat_repo = ChatRepository(db)
    return StreamingResponse(chat_repo.create_chat(user.id, chat_data, client), media_type='text/event-stream')


@router.post("/continue", response_model=ChatContinueResponse)
async def continue_chat(chat_data: ChatContinueData, user=Depends(current_active_user), db: AsyncSession = Depends(get_async_session), client=Depends(init_openai_client)):
    chat_repo = ChatRepository(db)
    return await chat_repo.continue_chat(user.id, client, chat_data)


@router.delete("/{chat_id}/")
async def delete_chat(chat_id: uuid.UUID, user=Depends(current_active_user),  db: AsyncSession = Depends(get_async_session)):
    chat_repo = ChatRepository(db)
    return await chat_repo.delete_chat(user.id, chat_id)


@router.get("/{chat_id}/", response_model=Chat)
async def get_chat(chat_id: uuid.UUID, user=Depends(current_active_user), db: AsyncSession = Depends(get_async_session)):
    chat_repo = ChatRepository(db)
    return await chat_repo.get_chat(user.id, chat_id)


@router.post("/new-search", response_model=ChatCreateResponse)
async def create_new_search(chat_data: TwitterChatData, user=Depends(current_active_user), db: AsyncSession = Depends(get_async_session), client=Depends(init_openai_client)):
    chat_repo = ChatRepository(db)
    return await chat_repo.create_search(user.id, chat_data, client)


@router.post("/continue-search", response_model=ChatContinueResponse)
async def continue_chat(chat_data: ChatContinueData, user=Depends(current_active_user), db: AsyncSession = Depends(get_async_session), client=Depends(init_openai_client)):
    chat_repo = ChatRepository(db)
    return await chat_repo.continue_chat(user.id, client, chat_data)
