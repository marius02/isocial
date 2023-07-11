import re
from dotenv import load_dotenv
from typing import Optional
from fastapi_users import BaseUserManager, InvalidPasswordException, exceptions
from fastapi import Request
from api.users.utils.email import send_welcome_email, send_forgot_email
from db.models.users import User
import uuid
import os

load_dotenv()


class UserManager(BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = os.getenv('USER_ISOCIAL_SECRET')
    verification_token_secret = os.getenv('USER_ISOCIAL_SECRET')

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        send_forgot_email(user.email, token)
        request.status = 200
        request.body = {"Description": "Email Sent"}

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print("In welcome email")
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

        # re.match(password_pattern, '-Secr3t.') # Returns Match object

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
