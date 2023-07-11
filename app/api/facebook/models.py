from pydantic import BaseModel


class FacebookCommentCreate(BaseModel):
    message: str
    user_id: str
