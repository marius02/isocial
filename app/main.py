import ssl

from app.api.chat.routes import router as chat_router
from app.api.notifications.routes import router as notification_router
from app.api.payments.routes import router as payment_router
from app.api.users.routes import router as user_router
from app.api.users.schemas import UserCreate, UserRead, UserUpdate
from app.api.users.services import auth_backend, fastapi_users
from app.db.db_config import create_db_and_tables
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI(title="iSocial")

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain("/path/to/cert.pem", keyfile="/path/to/key.pem")

origins = [
    "http://23.100.16.133",
    "http://23.100.16.133:8000",
    "https://23.100.16.133",
    "https://23.100.16.133:8000",
    "https://isocial.ai",
]

# Allow these methods to be used
methods = ["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"]

# Only these headers are allowed
headers = ["Content-Type", "Accept", "Authorization"]

app.add_middleware(SessionMiddleware, secret_key="some-random-string")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=methods,
    allow_headers=headers,
)
app.add_middleware(HTTPSRedirectMiddleware)

app.include_router(chat_router)
app.include_router(
    fastapi_users.get_auth_router(auth_backend, requires_verification=True),
    prefix="/auth/jwt",
    tags=["Authentication and authorization  "],
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
app.include_router(
    notification_router,
    prefix="/auth",
    tags=["Authentication and authorization"],
)
app.include_router(
    payment_router,
    prefix="/auth",
    tags=["Authentication and authorization"],
)


@app.on_event("startup")
async def on_startup():
    await create_db_and_tables()


@app.on_event("shutdown")
async def shutdown():
    pass
