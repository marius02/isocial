from datetime import datetime
from pydantic import BaseModel


class AddCreditRequest(BaseModel):
    amount: float
    success: str
    stripe_code: str
    datetime_now: datetime

    class Config:
        orm_mode = True
