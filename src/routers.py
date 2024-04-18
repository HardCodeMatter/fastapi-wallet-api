from fastapi import APIRouter

from auth.routers import router as auth_router
from wallet.routers import router as wallet_router


routers: list[APIRouter] = [
    auth_router,
    wallet_router,
]
