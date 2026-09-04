from fastapi import FastAPI

from app.api.charity_project import router as charity_project_router
from app.core.user import auth_backend, fastapi_users
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.api.donation import router as donation_router

app = FastAPI(
    title="Благотворительный фонд поддержки котиков QRKot",
    description="Сервис для поддержки котиков",
    version="0.1.0",
)

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)

app.include_router(charity_project_router)
app.include_router(donation_router)