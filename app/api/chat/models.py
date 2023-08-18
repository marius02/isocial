from pydantic import BaseModel
from api.youtube.models import YouTubeCommentResponse


class ChatCreate(BaseModel):
    youtube_comments: list[YouTubeCommentResponse] = []

    class Config:
        orm_mode = True
