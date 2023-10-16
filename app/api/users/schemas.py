from pydantic import BaseModel
import uuid

from fastapi_users import schemas


class UserRead(schemas.BaseUser[uuid.UUID]):
    pass


class UserCreate(schemas.BaseUserCreate):
    pass


class UserUpdate(schemas.BaseUserUpdate):
    pass


class AuthPassChange(BaseModel):
    email: str
    password: str
    new_password: str


class Auth(BaseModel):
    username: str
    password: str


class Question(BaseModel):
    question_id: str
    text: str
