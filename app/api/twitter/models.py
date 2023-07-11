from pydantic import BaseModel


class TwitterReplyCreate(BaseModel):
    reply: str
    user_id: str
