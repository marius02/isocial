from pydantic import BaseModel


class CommentsRequest(BaseModel):
    comments: list[str]