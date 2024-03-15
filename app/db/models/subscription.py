import uuid

from app.db.db_config import Base
from sqlalchemy import TIMESTAMP, Column, Float, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.sql import func


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, autoincrement=True, primary_key=True)
    price = Column(Float, nullable=False)
    tokens = Column(Integer, nullable=False)
    discount = Column(Float, nullable=False)


class UserSubscription(Base):
    __tablename__ = "usersubscription"

    id = Column(
        UUID(as_uuid=True),
        default=uuid.uuid4,
        nullable=False,
        unique=True,
        index=True,
        primary_key=True,
    )
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    sid = Column(Integer, ForeignKey("subscriptions.id"), primary_key=True)
    buy_date = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
    )
    balance = Column(Integer, default=0)
