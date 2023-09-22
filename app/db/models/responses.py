from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, ForeignKey, Text, Integer, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from db.db_config import Base


class Response(Base):
    __tablename__ = "responses"

    id = Column(UUID(as_uuid=True), default=uuid.uuid4,
                nullable=False, unique=True, index=True, primary_key=True)

    chat_id = Column(UUID(as_uuid=True), ForeignKey("all_chats.id"))

    question = Column(Text, nullable=True)
    response = Column(Text, nullable=True)
    date = Column(DateTime, server_default=func.now())
    tokens = Column(Integer, nullable=True)
    rating = Column(Integer, nullable=True)

    chat = relationship("Chat", back_populates="chats")
