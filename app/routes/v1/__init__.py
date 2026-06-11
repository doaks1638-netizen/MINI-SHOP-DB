from .cart import cart_router
from .categories import category_router
from .order import order_router
from .product import product_router
from .user import user_router
from .auth import auth_router
from fastapi import APIRouter

v1_router = APIRouter(prefix="/api/v1")
v1_router.include_router(cart_router)
v1_router.include_router(category_router)
v1_router.include_router(order_router)
v1_router.include_router(user_router)
v1_router.include_router(product_router)
v1_router.include_router(auth_router)
