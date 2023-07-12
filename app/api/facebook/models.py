from pydantic import BaseModel, HttpUrl
from typing import List


class FacebookCommentBase(BaseModel):
    text: str


class FacebookCommentCreate(FacebookCommentBase):
    pass


class FacebookComment(FacebookCommentBase):
    id: int

    class Config:
        orm_mode = True


class FacebookPostBase(BaseModel):
    post_url: HttpUrl
    post_text: str


class FacebookPostCreate(FacebookPostBase):
    pass


class FacebookPost(FacebookPostBase):
    id: int
    comments: List[FacebookComment] = []

    class Config:
        orm_mode = True
