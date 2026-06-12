from fastapi import APIRouter, Body, Depends, Query
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from app.models.cart_item import CartItem
from app.schemas import CartItemDTO
from app.database import DBsession
from app.services import check_user_product_exists, update_amount
from typing import Annotated
from uuid import UUID
from app.routes import page_number
from app.models.user import User
from app.models.product import Product
from app.routes import get_current_user

cart_router = APIRouter(tags=["CART"])


@cart_router.get("/cart/me", response_model=list[CartItemDTO])
async def get_user_cart(
    db: DBsession,
    page: page_number,
    user: Annotated[User, Depends(get_current_user)],
    product_id: Annotated[
        UUID, Query()
    ] = None,  # выборка товаров (если в корзине много товаров)
    search: Annotated[str, Query()] = None,
):
    query = (
        select(CartItem)
        .join(User, CartItem.user_id == User.id)
        .join(Product, CartItem.product_id == Product.id)
        .where(User.is_active == True, Product.is_active == True)
        .where(CartItem.user_id == user.id)
        .limit(30)
        .offset(30 * (page - 1))
    )

    if product_id is not None:
        stmt = query.where(Product.id == product_id)

    if search is not None:
        stmt = stmt.where(Product.name.like(f"%{search}%"))

    rez = await db.execute(query)
    return rez.scalars().all()


@cart_router.post("/cart", status_code=201, response_model=CartItemDTO)
async def create_new_cart(
    db: DBsession, item: CartItemDTO, user: Annotated[User, Depends(get_current_user)]
):
    await update_amount(db, item.product_id, -item.amount)
    stmt = insert(CartItem).values(**item.model_dump(), user_id=user.id)
    stmt = stmt.on_conflict_do_update(
        constraint=["user_id", "product_id"],
        set_=dict(amount=CartItem.amount + stmt.excluded.amount),
    )
    stmt = stmt.returning(CartItem)
    rez = await db.scalar(stmt)
    await db.commit()
    return rez


@cart_router.patch(
    "/cart/me/products/{product_id}",
    status_code=204,
)
async def change_product_amount(
    db: DBsession,
    user: Annotated[User, Depends(get_current_user)],
    new_amount: Annotated[int, Body(gt=0, embed=True)],
    product_id: UUID,
):
    cart_item = await check_user_product_exists(db, user.id, product_id)
    old_amount = cart_item.amount
    diff = new_amount - old_amount
    await update_amount(db, product_id, -diff)

    cart_item.amount = new_amount

    await db.commit()


@cart_router.delete(
    "/cart/me/products/{product_id}",
    status_code=204,
)
async def delete_product_from_cart(
    db: DBsession, user: Annotated[User, Depends(get_current_user)], product_id: UUID
):
    cart_item = await check_user_product_exists(db, user.id, product_id)
    old_amount = cart_item.amount
    await update_amount(db, product_id, old_amount)

    await db.delete(cart_item)

    await db.commit()
