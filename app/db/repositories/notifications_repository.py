from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.notification import Notification


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
        stmt = select(Notification).where(
            (Notification.user_id == user_id) & (Notification.read == False)
        )
        unread_notifications = await self.db.execute(stmt)
        notifications = unread_notifications.scalars().all()

        # UNCOMMENT THE BELOW CODE IF YOU NEED THE NOTIFICATIONS MARKED AS 'READ' AUTOMATICALLY
        # # Now that you have the unread notifications, mark them as read
        # for notification in notifications:
        #     notification.read = True

        # # Commit the changes to the database
        # await self.db.commit()

        return notifications
