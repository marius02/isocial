from sqlalchemy.ext.asyncio import AsyncSession
from api.youtube.models import YouTubeCommentCreate
from api.chat.models import ChatCreate
from db.models.youtube import YouTubeComment


class YouTubeRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_comment(self, comment: YouTubeCommentCreate, chat: ChatCreate):
        truncated_comments = comment.text[:2097]  # Truncate comments
        db_comment = YouTubeComment(
            url=comment.url,
            text=truncated_comments,
            chat_id=chat.id  # Associate the comment with the chat
        )
        self.db.add(db_comment)
        await self.db.commit()
        await self.db.refresh(db_comment)
        return db_comment

    async def get_comments(self, chat_id: int, skip: int = 0, limit: int = 10):
        return await self.db.query(YouTubeComment).filter(YouTubeComment.chat_id == chat_id).offset(skip).limit(limit).all()
