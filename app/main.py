from fastapi import FastAPI

from api.chat.routes import router as chat_router
from api.users.routes import router as user_router

from starlette.middleware.sessions import SessionMiddleware

from api.users.schemas import UserCreate, UserRead, UserUpdate
from api.users.utils.auth import auth_backend

from db.db_config import User, create_db_and_tables
from api.users.schemas import UserCreate, UserRead, UserUpdate
from api.users.services import auth_backend, fastapi_users
from fastapi.middleware.cors import CORSMiddleware

from dotenv import load_dotenv
import os

load_dotenv()

origins = os.getenv('CORS_ORIGIN')

# Allow these methods to be used
methods = ['GET', 'POST', 'OPTIONS', 'DELETE', 'PATCH', 'PUT']

# Only these headers are allowed
headers = ["Content-Type", "Authorization", "'Access-Control-Allow-Origin'"]


app = FastAPI(title='iSocial')
app.add_middleware(SessionMiddleware, secret_key="some-random-string")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=methods,
    allow_headers=headers
)

app.include_router(chat_router)
app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["Authentication and authorization"]
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["Authentication and authorization"],
)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["Authentication and authorization"],
)
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["Authentication and authorization"],
)
app.include_router(user_router)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["Users"],
)


@app.on_event("startup")
async def on_startup():
    await create_db_and_tables()


@app.on_event("shutdown")
async def shutdown():
    pass
