from app.db.db_config import Base
from sqlalchemy.sql import func
from sqlalchemy import Column, String, ForeignKey, TIMESTAMP, Float
from sqlalchemy.dialects.postgresql import UUID
import uuid


class Credit(Base):
    __tablename__ = "credits"

    id = Column(UUID(as_uuid=True), default=uuid.uuid4,
                nullable=False, unique=True, index=True, primary_key=True)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    amount = Column(Float, default=0.0)
    date = Column(TIMESTAMP(timezone=True), server_default=func.now())
    success = Column(String, nullable=True)
    stripe_code = Column(String, nullable=True)
