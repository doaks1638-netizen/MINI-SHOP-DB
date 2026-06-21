from fastapi import APIRouter, Body, Depends
from sqlalchemy import select, func
from app.models import CartItem, Product, User
from app.schemas import AdminCart, AdminCartItemDTO
from app.database import DBsession
from app.services import check_user_product_exists, update_amount
from typing import Annotated
from uuid import UUID
from app.routes import page_number
from app.routes import get_current_admin

admin_cart_router = APIRouter(
    prefix="/admin/cart", dependencies=[Depends(get_current_admin)], tags=["ADMIN"]
)


@admin_cart_router.get("/", response_model=list[AdminCart])
async def get_all_carts(db: DBsession, page: page_number):
    query = (
        select(
            CartItem.user_id,
            func.count(CartItem.product_id).label("total_products"),
            func.sum(CartItem.amount).label("total_items"),
            User.is_active.label("is_user_active"),
        )
        .select_from(CartItem)
        .join(User, CartItem.user_id == User.id)
        .join(Product, CartItem.product_id == Product.id)
        .group_by(CartItem.user_id, User.is_active)
        .limit(30)
        .offset(30 * (page - 1))
    )
    rez = await db.execute(query)
    return rez.mappings().all()


@admin_cart_router.get("/{user_id}", response_model=list[AdminCartItemDTO])
async def get_user_cart(db: DBsession, page: page_number, user_id: UUID):
    query = (
        select(
            CartItem.product_id, CartItem.amount, User.is_active.label("is_user_active")
        )
        .join(User, User.id == CartItem.user_id)
        .where(CartItem.user_id == user_id)
        .limit(30)
        .offset(30 * (page - 1))
    )
    rez = await db.execute(query)
    return rez.mappings().all()


@admin_cart_router.patch(
    "/{user_id}/products/{product_id}",
    status_code=204,
)
async def change_product_amount(
    db: DBsession,
    new_amount: Annotated[int, Body(gt=0, embed=True)],
    product_id: UUID,
    cart_item=Depends(check_user_product_exists),
):
    old_amount = cart_item.amount
    diff = new_amount - old_amount
    await update_amount(db, product_id, -diff)

    cart_item.amount = new_amount

    await db.commit()


@admin_cart_router.delete(
    "/{user_id}/products/{product_id}",
    status_code=204,
)
async def delete_product_from_cart(
    db: DBsession,
    product_id: UUID,
    cart_item=Depends(check_user_product_exists),
):
    old_amount = cart_item.amount
    await update_amount(db, product_id, old_amount)

    await db.delete(cart_item)

    await db.commit()
