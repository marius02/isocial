from pydantic import BaseModel


class FacebookCommentCreate(BaseModel):
    url: str
    text: str
    
    class Config:
        orm_mode = True


class FacebookCommentResponse(FacebookCommentCreate):
    question: str = None
    answer: str = None
    
    class Config:
        orm_mode = True