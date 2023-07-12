from pydantic import BaseModel


class CommentsRequest(BaseModel):
    comments: str


class SummaryResponse(BaseModel):
    summary: str
