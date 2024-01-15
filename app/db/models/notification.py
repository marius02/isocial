from app.db.db_config import Base
from sqlalchemy import Column, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), default=uuid.uuid4,
                nullable=False, unique=True, index=True, primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    text = Column(String, nullable=True)
    read = Column(Boolean, default=False)
