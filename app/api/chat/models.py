from datetime import datetime
from typing import Optional
import uuid
from pydantic import BaseModel, HttpUrl


class YouTubeChatData(BaseModel):
    chat_id: uuid.UUID
    url: HttpUrl = None
    platform: str = "YouTube"
    question: str = None


class TwitterChatData(BaseModel):
    chat_id: uuid.UUID
    platform: str = "X"
    search: str
    date: datetime
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
    date: datetime


class Chat(BaseModel):
    id: uuid.UUID
    platform: str = None
    created_at: datetime
    url: str = None
    search: str = None
    img_url1: Optional[str] = None
    img_url2: Optional[str] = None
    img_url3: Optional[str] = None
    img_url4: Optional[str] = None
    chats: list[ChatResponse]

    class Config:
        orm_mode = True
        exclude = ("url",
                   "search",
                   "img_url1",
                   "img_url2",
                   "img_url3",
                   "img_url4")

    def dict(self, *args, **kwargs):
        kwargs['exclude_unset'] = True  # Only include fields with values
        return super().dict(*args, **kwargs)


class ChatContinueData(BaseModel):
    chat_id: uuid.UUID
    question: str = None
    date: datetime


class ChatShort(BaseModel):
    id: uuid.UUID
    url: str = None
    created_at: datetime

    class Config:
        orm_mode = True


class ChatCreateResponse(BaseModel):
    id: uuid.UUID
    platform: str = None
    date: datetime
    img_url1: Optional[str] = None
    img_url2: Optional[str] = None
    img_url3: Optional[str] = None
    img_url4: Optional[str] = None
    response: str = None

    class Config:
        orm_mode = True


class AllChats(BaseModel):
    chats: list[ChatShort]

    class Config:
        orm_mode = True
