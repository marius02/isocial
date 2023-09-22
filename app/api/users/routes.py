from fastapi import APIRouter, HTTPException, Depends, status
from fastapi_users import models
from fastapi_users.manager import BaseUserManager

from api.users.schemas import AuthPassChange, Auth

from db.db_config import User
from api.users.services import get_user_manager, current_active_user


router = APIRouter(prefix="/auth", tags=["Authentication and authorization"])


@router.post('/changepassword/')
async def password_change(pass_change: AuthPassChange, user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager)):

    auth = Auth(username=pass_change.email, password=pass_change.password)

    valid_user = await user_manager.authenticate(auth)

    if not valid_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid username or password")

    await user_manager.reset_password_user(valid_user, pass_change.new_password)

    return {"message": f"Password updated successfully "}


@router.get("/authenticated-route")
async def authenticated_route(user: User = Depends(current_active_user)):
    return {"message": f"Hello {user.email}!"}
