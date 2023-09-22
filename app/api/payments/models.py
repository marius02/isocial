from pydantic import BaseModel


class AddCreditRequest(BaseModel):
    amount: float
    success: str
    stripe_code: str

    class Config:
        orm_mode = True