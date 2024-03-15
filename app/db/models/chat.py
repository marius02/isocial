import uuid
from app.db.db_config import Base
from sqlalchemy import TIMESTAMP, Column, ForeignKey, String, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID


class Chat(Base):
    __tablename__ = "all_chats"

    id = Column(UUID(as_uuid=True), default=uuid.uuid4,
                nullable=False, unique=True, index=True, primary_key=True)
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
   
    user = relationship("User", back_populates="all_chats")
    url = Column(String, nullable=True)
    commentblob = Column(Text, nullable=True)
    delete = Column(String, default='N')
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    platform = Column(String)
    img_url1 = Column(Text, nullable=True)
    img_url2 = Column(Text, nullable=True)
    img_url3 = Column(Text, nullable=True)
    img_url4 = Column(Text, nullable=True)

    chats = relationship(
        "Response",
        back_populates="chat",
    )

    def get_chats(self):
        return self.chats
