import uuid
from db.db_config import Base
from sqlalchemy import Column, ForeignKey, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID


class Chat(Base):
    __tablename__ = "all_chats"

    id = Column(UUID(as_uuid=True), default=uuid.uuid4,
                nullable=False, unique=True, index=True, primary_key=True)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    user = relationship("User", back_populates="all_chats")

    url = Column(String)

    commentblob = Column(Text, nullable=True)

    chats = relationship(
        "Response",
        back_populates="chat",
    )

    def get_chats(self):
        return self.chats