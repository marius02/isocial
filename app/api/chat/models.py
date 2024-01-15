import uuid
from pydantic import BaseModel, HttpUrl


class ChatData(BaseModel):
    chat_id: uuid.UUID
    url: HttpUrl
    platform: str
    question: str = None


class ChatContinueData(BaseModel):
    chat_id: uuid.UUID
    platform: str
    question: str = None


class ChatResponse(BaseModel):
    id: uuid.UUID
    question: str = None
    response: str = None

    class Config:
        orm_mode = True


class ChatContinueResponse(ChatResponse):
    chat_id: uuid.UUID


class Chat(BaseModel):
    id: uuid.UUID
    url: str
    chats: list[ChatResponse]

    class Config:
        orm_mode = True


class ChatShort(BaseModel):
    id: uuid.UUID
    url: str

    class Config:
        orm_mode = True


class ChatCreateResponse(BaseModel):
    chat_id: uuid.UUID
    id: uuid.UUID
    response: str = None

    class Config:
        orm_mode = True


class AllChats(BaseModel):
    chats: list[ChatShort]

    class Config:
        orm_mode = True
