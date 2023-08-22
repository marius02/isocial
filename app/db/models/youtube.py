from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
import uuid

from db.db_config import Base


class YouTubeComment(Base):
    __tablename__ = "youtube_comments"

    id = Column(UUID(as_uuid=True), default=uuid.uuid4,
                nullable=False, unique=True, index=True, primary_key=True)
    url = Column(String)
    text = Column(Text)
    question = Column(Text, nullable=True)
    answer = Column(Text, nullable=True)

    chat_id = Column(UUID(as_uuid=True), ForeignKey("chats.id"))

    chat = relationship("Chat", back_populates="youtube_comments")
