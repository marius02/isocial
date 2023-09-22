from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.models.notification import Notification


class NotificationRepositoryAsync:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_notification(self, user_id: str, text: str):
        notification = Notification(user_id=user_id, text=text)
        self.db.add(notification)
        await self.db.commit()
        await self.db.refresh(notification)
        return notification

    async def get_notifications_by_user_id(self, user_id: str):
        stmt = select(Notification).where(Notification.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()
