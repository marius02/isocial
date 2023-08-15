from sqlalchemy import Column, Integer, String, URL
from sqlalchemy.orm import relationship

from db.db_config import Base


class FacebookComment(Base):
    __tablename__ = "facebook_comments"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)

    post = relationship("FacebookPost", back_populates="comments")


class FacebookPost(Base):
    __tablename__ = "facebook_posts"

    id = Column(Integer, primary_key=True, index=True)
    post_url = Column(String)

    comments = relationship("FacebookComment", back_populates="post")
