from fastapi import APIRouter

from auth.routers import router as auth_router


routers: list[APIRouter] = [
    auth_router,
]
