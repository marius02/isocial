from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.credit import Credit
from app.db.models.subscription import Subscription, UserSubscription
from sqlalchemy.future import select
from fastapi import HTTPException
from datetime import datetime


class PaymentRepositoryAsync:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_credit(self, user_id: str, amount: str, success: str, stripe_code: str, date: datetime):
        credit = Credit(user_id=user_id, amount=amount,
                        success=success, date=date, stripe_code=stripe_code)
        self.db.add(credit)
        await self.db.commit()
        await self.db.refresh(credit)
        return credit


class SubscriptionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_subscription(self, user_id: str):
        stmt = select(UserSubscription).filter(
            UserSubscription.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar()

    async def map_subscription_with_amount(self, amount: float):
        stmt = select(Subscription).filter(Subscription.price == amount)
        result = await self.db.execute(stmt)
        subscription = result.scalar()
        return subscription

    async def increase_user_balance(self, user_id: str, amount: float):
        existing_user_subscription = await self.get_user_subscription(user_id)
        subscription = await self.map_subscription_with_amount(amount)

        if subscription:
            bought_tokens = subscription.tokens
            subscription_id = subscription.id

            if existing_user_subscription:
                existing_user_subscription.balance += bought_tokens
                await self.db.commit()
                await self.db.refresh(existing_user_subscription)
                return existing_user_subscription
            else:
                new_user_subscription = UserSubscription(user_id=user_id,
                                                         sid=subscription_id,
                                                         balance=bought_tokens)
                self.db.add(new_user_subscription)
                await self.db.commit()
                await self.db.refresh(new_user_subscription)
                return new_user_subscription
        else:
            raise HTTPException(
                status_code=404, detail=f"Subscription for the amount {amount} not found")

    async def decrease_user_balance(self, user_id: str, tokens: int):
        existing_user_subscription = await self.get_user_subscription(user_id)

        if existing_user_subscription:
            existing_user_subscription.balance -= tokens
            await self.db.commit()
            await self.db.refresh(existing_user_subscription)
        else:
            raise HTTPException(
                status_code=404, detail="Subscription not found")

    async def get_user_balance(self, user_id: str):
        user_subscription = await self.get_user_subscription(user_id)
        if user_subscription:
            return user_subscription.balance
        else:
            raise HTTPException(
                status_code=404, detail="User not found or has no subscription")
