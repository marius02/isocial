from sqlalchemy import Column, Integer, String
from db.base import Base


class TwitterReply(Base):
    __tablename__ = "twitter_replies"

    id = Column(Integer, primary_key=True, index=True)
    message = Column(String)
