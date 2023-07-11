from sqlalchemy import Column, Integer, String
from db.base import Base


class FacebookComment(Base):
    __tablename__ = "facebook_comments"

    id = Column(Integer, primary_key=True, index=True)
    message = Column(String)
    # Add more fields as needed
