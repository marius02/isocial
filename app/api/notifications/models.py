from uuid import UUID
from pydantic import BaseModel


class NotificationResponse(BaseModel):
    id: UUID
    text: str

    class Config:
        orm_mode = True
