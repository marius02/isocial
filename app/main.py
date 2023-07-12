from fastapi import FastAPI

from api.facebook.routes import router as facebook_router
from api.instagram.routes import router as instagram_router
from api.youtube.routes import router as youtube_router
from api.twitter.routes import router as twitter_router
from api.openai.routes import router as openai_router

from db.models.users import User
from db.base import create_db_and_tables
from fastapi import HTTPException, Depends, status
from fastapi_users import FastAPIUsers, models
from fastapi_users.manager import BaseUserManager
from api.users.models import UserCreate, UserRead, UserUpdate, AuthPassChange, Auth
from api.users.utils.auth import get_user_manager, current_active_user
from api.users.utils.auth import auth_backend
import uuid


app = FastAPI(title='iSocial')

fastapi_users = FastAPIUsers[User, uuid.UUID](get_user_manager, [auth_backend])

app.include_router(facebook_router)
app.include_router(instagram_router)
app.include_router(youtube_router)
app.include_router(twitter_router)
app.include_router(openai_router)
app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)


@app.post('/auth/changepassword/')
async def password_change(pass_change: AuthPassChange, user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager)):
    # user_db = get_user_db(get_async_session())
    auth = Auth(username=pass_change.email, password=pass_change.password)

    valid_user = await user_manager.authenticate(auth)

    if not valid_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid username or password")

    updated_user = await user_manager.reset_password_user(valid_user, pass_change.new_password)
    print(updated_user)

    return {"message": f"Password updated successfully "}

    # make this async


@app.get("/authenticated-route")
async def authenticated_route(user: User = Depends(current_active_user)):
    return {"message": f"Hello {user.email}!"}


@app.on_event("startup")
async def startup():
    # Perform any startup tasks, such as establishing database connections
    pass


@app.on_event("shutdown")
async def shutdown():
    # Perform any shutdown tasks, such as closing database connections
    await create_db_and_tables()
