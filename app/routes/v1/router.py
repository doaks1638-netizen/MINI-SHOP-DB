from fastapi import APIRouter
from app.routes.v1 import cart_router, category_router

v1_router = APIRouter(prefix="/api/v1")
v1_router.include_router(cart_router)
v1_router.include_router(category_router)
