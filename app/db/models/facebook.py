from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship

from db.db_config import Base


class FacebookComment(Base):
    __tablename__ = "facebook_comments"

    id = Column(Integer, primary_key=True, index=True)
    chatid = Column(String, index=True)
    url = Column(String)
    text = Column(Text)
    question = Column(Text, nullable=True)
    answer = Column(Text, nullable=True)