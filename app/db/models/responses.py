import uuid

from app.db.db_config import Base
from sqlalchemy import TIMESTAMP, Column, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class Response(Base):
    __tablename__ = "responses"

    id = Column(
        UUID(as_uuid=True),
        default=uuid.uuid4,
        nullable=False,
        unique=True,
        index=True,
        primary_key=True,
    )

    chat_id = Column(UUID(as_uuid=True), ForeignKey("all_chats.id"))

    question = Column(Text, nullable=True)
    response = Column(Text, nullable=True)
    search = Column(Text, nullable=True)
    date = Column(TIMESTAMP(timezone=True), server_default=func.now())
    tokens = Column(Integer, nullable=True)
    rating = Column(Integer, nullable=True)

    chat = relationship("Chat", back_populates="chats")
