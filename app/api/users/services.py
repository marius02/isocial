import re
from dotenv import load_dotenv
from typing import Optional
from fastapi_users import (BaseUserManager,
                           FastAPIUsers,
                           InvalidPasswordException,
                           exceptions,
                           UUIDIDMixin,
                           )
from fastapi_users.db import SQLAlchemyUserDatabase
from app.db.db_config import User, get_user_db

from fastapi import Depends, Request
from app.api.users.utils.email import send_welcome_email
from app.db.models.users import User
import uuid
import os

from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)


load_dotenv()

SECRET = os.getenv('USER_ISOCIAL_SECRET')


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")
        await self.request_verify(user, request)

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        send_forgot_email(user.email, token)
        request.status = 200
        request.body = {"Description": "Email Sent"}

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        send_welcome_email(user.email, token)
        request.status = 200
        request.body = {"Description": "Email Sent"}

    async def validate_password(
            self, password: str, user) -> None:

        if len(password) > 16:
            raise InvalidPasswordException(
                reason="Password should be at most 16 characters "
            )

        password_pattern = "^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$"

        print(re.match(password_pattern, password))
        if not re.match(password_pattern, password):  # Returns None
            raise InvalidPasswordException(
                reason="Password does not meet minimum criteria "
            )

    async def reset_password_user(
        self, user, password: str, request: Optional[Request] = None
    ):
        """
        Reset password given a user and new password 
        """

        if not user.is_active:
            raise exceptions.UserInactive()

        updated_user = await self._update(user, {"password": password})

        await self.on_after_reset_password(user, request)

        return updated_user


async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)


bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, uuid.UUID](get_user_manager, [auth_backend])


current_active_user = fastapi_users.current_user(active=True)
