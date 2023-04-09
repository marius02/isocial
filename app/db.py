from typing import AsyncGenerator

from fastapi import Depends
from fastapi_users.db import SQLAlchemyBaseUserTableUUID, SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Identity, UUID
from sqlalchemy.orm import relationship

#from .database import Base


DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost/postgres"


class Base(DeclarativeBase):
    pass


class User(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "users2"
    pass


class VideoReq(Base):
    __tablename__ = "videoreq3"
    id = Column(Integer, Identity(start=42, cycle=True),
                primary_key=True, index=True)
    sessionid = Column(UUID, index=True)
    email = Column(String)
    videoid = Column(String)
    user_id = Column(UUID, ForeignKey(User.id))


engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)
