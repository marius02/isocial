
from fastapi import Depends, FastAPI, HTTPException

from fastapi_users import exceptions, models
from fastapi_users.manager import BaseUserManager, UserManagerDependency

import contextlib
from sqlalchemy import insert

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


from pydantic import BaseModel

from fastapi import status

import requests
from fastapi.security import OAuth2PasswordRequestForm
from app.db import User, VideoReq, create_db_and_tables, get_async_session
from app.schemas import UserCreate, UserRead, UserUpdate
from app.users import auth_backend, current_active_user, fastapi_users, get_user_db, get_user_manager
from summarize import summarize


class AuthPassChange(BaseModel):
    email: str
    password: str
    new_password: str


class Auth(BaseModel):
    username: str
    password: str


app = FastAPI()

app.include_router(
    fastapi_users.get_auth_router(auth_backend, requires_verification=True), prefix="/auth/jwt", tags=["auth"]

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


@app.get('/')
def hello():
    return 'Hello, World what!'


@app.get('/summary/{video_id}')
async def summary(video_id):
    return summarize(video_id=video_id)


# @app.get('/auth/verify2/{token}')
# async def verify2(token: str):
#    url = 'http://localhost:8000/auth/verify'
#    myobj = {'token': token}

#    x = await requests.post(url, json=myobj)

#    if x.status_code == 200:
#        return "Account verified"
#    else:
#        return "Error - Invalid token "


@app.post('/auth/changepassword/')
async def password_change(pass_change: AuthPassChange, user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager)):
    #user_db = get_user_db(get_async_session())
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
def authenticated_route(user: User = Depends(current_active_user)):
    return {"message": f"Hello {user.email}!"}


@ app.get("/summarize/{video_id}")
def summary_(video_id: str, user: User = Depends(current_active_user)):

    DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost/postgres"
    engine = create_async_engine(DATABASE_URL)
    session = async_sessionmaker(engine, expire_on_commit=False)
    d = session.begin()

    summary = summarize(video_id=video_id)

    stmt = insert(VideoReq).values(email=user.email,
                                   videoid=video_id, summary=str(summary))

    d.async_session.execute(stmt)

    return summary


@ app.on_event("startup")
async def on_startup():
    # Not needed if you setup a migration system like Alembic
    await create_db_and_tables()
