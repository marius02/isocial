from pydantic import BaseModel


class YouTubeCommentCreate(BaseModel):
    url: str
    text: str
    chat: str


class YouTubeCommentResponse(BaseModel):
    id: int
    url: str
    text: str
    question: str = None
    answer: str = None

    class Config:
        orm_mode = True
