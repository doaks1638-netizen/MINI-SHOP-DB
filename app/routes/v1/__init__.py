from .user_actions.cart import cart_router
from .user_actions.categories import category_router
from .user_actions.order import order_router
from .user_actions.product import product_router
from .user_actions.user import user_router
from .auth import auth_router
from .admin_actions.user_admin import admin_user_router
from .admin_actions.cart_admin import admin_cart_router
from .admin_actions.order_admin import admin_order_router
from .admin_actions.product_admin import admin_product_router
from .admin_actions.category_admin import admin_category_router
from .creator_actions.creator_actions import creator_router
from fastapi import APIRouter

v1_router = APIRouter(prefix="/api/v1")
v1_router.include_router(cart_router)
v1_router.include_router(category_router)
v1_router.include_router(order_router)
v1_router.include_router(user_router)
v1_router.include_router(product_router)
v1_router.include_router(auth_router)
v1_router.include_router(admin_user_router)
v1_router.include_router(admin_cart_router)
v1_router.include_router(admin_order_router)
v1_router.include_router(admin_product_router)
v1_router.include_router(creator_router)
v1_router.include_router(admin_category_router)
