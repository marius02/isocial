from app.api.users.services import current_active_user
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.db_config import get_async_session
from app.db.repositories.notifications_repository import NotificationRepositoryAsync
from .models import NotificationResponse

router = APIRouter()


@router.get("/notifications/list", response_model=list[NotificationResponse])
async def get_notifications(user=Depends(current_active_user), db: AsyncSession = Depends(get_async_session)):
    notification_repo = NotificationRepositoryAsync(db)
    notifications = await notification_repo.get_notifications_by_user_id(user.id)

    return notifications
