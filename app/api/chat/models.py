import uuid
from datetime import datetime as dt
from typing import Optional

from pydantic import BaseModel, HttpUrl


class YouTubeChatData(BaseModel):
    chat_id: uuid.UUID
    url: str = None
    platform: str = "YouTube"
    question: str = None
    created_at: dt


class TwitterChatData(BaseModel):
    chat_id: uuid.UUID
    platform: str = "X"
    search: str
    date: dt
    question: str = None

    class Config:
        orm_mode = True


class ChatResponse(BaseModel):
    id: uuid.UUID
    question: str = None
    response: str = None

    class Config:
        orm_mode = True


class ChatContinueResponse(ChatResponse):
    chat_id: uuid.UUID
    date: dt


class Chat(BaseModel):
    id: uuid.UUID
    platform: str = None
    created_at: Optional[dt]
    url: str = None
    search: str = None
    img_url1: Optional[str] = None
    img_url2: Optional[str] = None
    img_url3: Optional[str] = None
    img_url4: Optional[str] = None
    chats: list[ChatResponse]

    class Config:
        orm_mode = True
        exclude = ("url", "search", "img_url1", "img_url2", "img_url3", "img_url4")

    def dict(self, *args, **kwargs):
        kwargs["exclude_unset"] = True  # Only include fields with values
        return super().dict(*args, **kwargs)


class ChatContinueData(BaseModel):
    chat_id: uuid.UUID
    question: str = None
    date: dt


class ChatShort(BaseModel):
    id: uuid.UUID
    url: str = None
    created_at: dt

    class Config:
        orm_mode = True


class ChatCreateResponse(BaseModel):
    id: uuid.UUID
    platform: str = None
    date: dt
    img_url1: Optional[str] = None
    img_url2: Optional[str] = None
    img_url3: Optional[str] = None
    img_url4: Optional[str] = None
    response: str = None

    class Config:
        orm_mode = True
        exclude = ("img_url1", "img_url2", "img_url3", "img_url4")

    def dict(self, *args, **kwargs):
        kwargs["exclude_unset"] = True  # Only include fields with values
        return super().dict(*args, **kwargs)


class AllChats(BaseModel):
    chats: list[ChatShort]

    class Config:
        orm_mode = True
