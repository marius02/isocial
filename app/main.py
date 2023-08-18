from fastapi import FastAPI

from api.facebook.routes import router as facebook_router
from api.instagram.routes import router as instagram_router
from api.youtube.routes import router as youtube_router
from api.twitter.routes import router as twitter_router
from api.openai.routes import router as openai_router
from api.chat.routers import router as chat_router

from fastapi import HTTPException, Depends, status
from fastapi_users import models
from fastapi_users.manager import BaseUserManager

from starlette.middleware.sessions import SessionMiddleware

from api.users.schemas import UserCreate, UserRead, UserUpdate, AuthPassChange, Auth
from api.users.utils.auth import get_user_manager, current_active_user
from api.users.utils.auth import auth_backend

from db.db_config import User, create_db_and_tables
from api.users.schemas import UserCreate, UserRead, UserUpdate
from api.users.services import auth_backend, current_active_user, fastapi_users


app = FastAPI(title='iSocial')
app.add_middleware(SessionMiddleware, secret_key="some-random-string")

app.include_router(chat_router)
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

    await user_manager.reset_password_user(valid_user, pass_change.new_password)

    return {"message": f"Password updated successfully "}


@app.get("/authenticated-route")
async def authenticated_route(user: User = Depends(current_active_user)):
    return {"message": f"Hello {user.email}!"}


@app.on_event("startup")
async def on_startup():
    await create_db_and_tables()


@app.on_event("shutdown")
async def shutdown():
    pass