import os
import uuid
from contextlib import asynccontextmanager

import openai
from app.api.chat.models import (
    AllChats,
    ChatContinueData,
    ChatContinueResponse,
    ChatCreateResponse,
    TwitterChatData,
    YouTubeChatData,
)
from app.api.users.services import current_active_user
from app.db.db_config import get_async_session
from app.db.repositories.chat_repository import ChatRepository
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession


def init_openai_client():
    client = openai.Client()
    client.api_key = os.getenv("OPENAI_API_KEY")
    return client


initial_dependencies = {}


@asynccontextmanager
async def lifespan(app: APIRouter):
    initial_dependencies["openai_client"] = init_openai_client()
    yield
    initial_dependencies.clear()


router = APIRouter(prefix="/chat", tags=["Chat"])


@router.get(
    "/list",
    description="Get a list of chats for the authenticated user",
    response_model=AllChats,
)
async def get_user_chats(
    user=Depends(current_active_user), db: AsyncSession = Depends(get_async_session)
):
    chat_repo = ChatRepository(db)
    return await chat_repo.get_user_chats(user.id)


@router.post(
    "",
    description="Create a new chat based on YouTube chat data",
    response_model=ChatCreateResponse,
)
async def create_new_chat(
    chat_data: YouTubeChatData,
    user=Depends(current_active_user),
    db: AsyncSession = Depends(get_async_session),
    client=Depends(init_openai_client),
):
    chat_repo = ChatRepository(db)
    results = await chat_repo.create_chat(user.id, chat_data, client)
    return results


@router.post(
    "/continue",
    description="Continue an existing chat using provided chat data",
    response_model=ChatContinueResponse,
)
async def continue_chat(
    chat_data: ChatContinueData,
    user=Depends(current_active_user),
    db: AsyncSession = Depends(get_async_session),
    client=Depends(init_openai_client),
):
    chat_repo = ChatRepository(db)
    return await chat_repo.continue_chat(user.id, client, chat_data)


@router.delete(
    "/{chat_id}",
    description="Delete a chat with the specified chat ID associated with the authenticated user",
)
async def delete_chat(
    chat_id: uuid.UUID,
    user=Depends(current_active_user),
    db: AsyncSession = Depends(get_async_session),
):
    chat_repo = ChatRepository(db)
    return await chat_repo.delete_chat(user.id, chat_id)


@router.get(
    "/{chat_id}",
    description="Retrieve details of a specific chat using its chat ID",
)
async def get_chat(
    chat_id: uuid.UUID,
    user=Depends(current_active_user),
    db: AsyncSession = Depends(get_async_session),
):
    chat_repo = ChatRepository(db)
    return await chat_repo.get_chat(user.id, chat_id)


@router.post(
    "/new-search",
    description="Create a new chat based on Twitter chat data for search",
    response_model=ChatCreateResponse,
)
async def create_new_search(
    chat_data: TwitterChatData,
    user=Depends(current_active_user),
    db: AsyncSession = Depends(get_async_session),
    client=Depends(init_openai_client),
):
    chat_repo = ChatRepository(db)
    return await chat_repo.create_search(user.id, chat_data, client)


@router.post(
    "/continue-search",
    description="Continue an existing search-based chat using provided chat data",
    response_model=ChatContinueResponse,
)
async def continue_search(
    chat_data: ChatContinueData,
    user=Depends(current_active_user),
    db: AsyncSession = Depends(get_async_session),
    client=Depends(init_openai_client),
):
    chat_repo = ChatRepository(db)
    return await chat_repo.continue_search(user.id, client, chat_data)
