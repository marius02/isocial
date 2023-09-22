from httpx import delete
from api.users.services import current_active_user
from fastapi import APIRouter, HTTPException, Depends
from .models import AddCreditRequest
from db.db_config import get_async_session
from db.repositories.notifications_repository import NotificationRepositoryAsync
from db.repositories.payments_repository import PaymentRepositoryAsync, SubscriptionRepository
from sqlalchemy.ext.asyncio import AsyncSession
import datetime


router = APIRouter()


@router.post("/account/addcredit")
async def add_credit(request_data: AddCreditRequest,
                     user=Depends(current_active_user),
                     db: AsyncSession = Depends(get_async_session)):

    # Validate if success code is "y" or "n"
    if request_data.success not in ["y", "n"]:
        raise HTTPException(status_code=400, detail="Invalid success code")

    if request_data.success == "n":
        return {
            "detail": {
                "code": "PURCHASE_FAILED",
                "reason": "Purchase was not successful"
            }
        }

    # Add bought tokens into user balance
    subscription_repo = SubscriptionRepository(db)
    subscription = await subscription_repo.increase_user_balance(user.id, amount=request_data.amount)

    date_time = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M")

    # Initialize the PaymentRepositoryAsync with the database session
    payment_repo = PaymentRepositoryAsync(db)

    # Add credit using the repository
    await payment_repo.add_credit(
        user_id=user.id,
        amount=request_data.amount,
        success=request_data.success,
        stripe_code=request_data.stripe_code,
    )

    # Initialize the NotificationRepositoryAsync with the database session
    notification_repo = NotificationRepositoryAsync(db)

    # Create a notification for the successful purchase
    tokens_bought = await subscription_repo.map_subscription_with_amount(amount=request_data.amount)
    await notification_repo.create_notification(
        user_id=user.id,
        text=f"You purchased {tokens_bought.tokens} tokens on {date_time} with USD{request_data.amount} payment"
    )

    return {
        "detail": {
            "code": "PURCHASE_SUCCESSFUL",
            "reason": f"{tokens_bought.tokens} tokens were added to your balance"
        }
    }


@router.post("/account/balance")
async def get_user_balance(user=Depends(current_active_user),
                           db: AsyncSession = Depends(get_async_session)):
    subscription_repo = SubscriptionRepository(db)
    balance = await subscription_repo.get_user_balance(user.id)
    return {
        "balance": balance
    }
