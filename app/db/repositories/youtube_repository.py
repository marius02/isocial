from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from api.youtube.models import YouTubeCommentCreate
from db.models.youtube import YouTubeComment
from db.models.chat import Chat
from sqlalchemy.future import select
import uuid


class YouTubeRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_comment(self, comment: YouTubeCommentCreate, chat_id: uuid.UUID):
        truncated_comments = comment.text[:2097]
        db_comment = YouTubeComment(
            url=comment.url,
            text=truncated_comments,
            chat_id=chat_id
        )
        self.db.add(db_comment)
        await self.db.commit()
        await self.db.refresh(db_comment)
        return db_comment

    async def get_comments_by_chat_id(self, user_id: uuid.UUID, chat_id: uuid.UUID):
        stmt = select(YouTubeComment).join(YouTubeComment.chat).where(
            (Chat.id == chat_id) & (Chat.user_id == user_id)
        )
        result = await self.db.execute(stmt)
        comments = result.scalars().all()

        if comments:
            return comments
        else:
            raise HTTPException(status_code=404, detail="Comments not found")

    async def get_comment(self, user_id: uuid.UUID, comment_id: uuid.UUID):
        stmt = select(YouTubeComment).join(YouTubeComment.chat).where(
            (id == comment_id) & (Chat.user_id == user_id)
        )
        result = await self.db.execute(stmt)
        comment = result.scalar()

        if comment:
            return comment
        else:
            raise HTTPException(status_code=404, detail="Comments not found")
