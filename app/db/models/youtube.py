from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from db.db_config import Base
from db.models.chat import Chat


class YouTubeComment(Base):
    __tablename__ = "youtube_comments"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String)
    text = Column(Text)
    question = Column(Text, nullable=True)
    answer = Column(Text, nullable=True)

    # Relationship to Chat
    chat_id = Column(UUID(as_uuid=True), ForeignKey("chats.id"))

    chat = relationship("Chat", back_populates="youtube_comments")
