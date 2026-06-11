from fastapi import APIRouter, Body, Depends
from sqlalchemy import select, func
from sqlalchemy.dialects.postgresql import insert
from app.models.cart_item import CartItem
from app.schemas import Cart, CartItemDTO
from app.database import DBsession
from app.services import check_user_product_exists, update_amount
from typing import Annotated
from uuid import UUID
from app.routes import page_number
from app.models.user import User
from app.models.product import Product

cart_router = APIRouter(tags=["CART"])


@cart_router.get("/cart", response_model=list[Cart])
async def get_all_carts(db: DBsession, page: page_number):
    query = (
        select(
            CartItem.user_id,
            func.count(CartItem.product_id).label("total_products"),
            func.sum(CartItem.amount).label("total_items"),
        )
        .select_from(CartItem)
        .join(User, CartItem.user_id == User.id)
        .join(Product, CartItem.product_id == Product.id)
        .where(User.is_active == True, Product.is_active == True)
        .group_by(CartItem.user_id)
        .limit(30)
        .offset(30 * (page - 1))
    )
    rez = await db.execute(query)
    return rez.mappings().all()


@cart_router.get("/cart/{user_id}", response_model=list[CartItemDTO])
async def get_user_cart(db: DBsession, page: page_number, user_id: UUID):
    query = (
        select(CartItem)
        .join(User, CartItem.user_id == User.id)
        .join(Product, CartItem.product_id == Product.id)
        .where(User.is_active == True, Product.is_active == True)
        .where(CartItem.user_id == user_id)
        .limit(30)
        .offset(30 * (page - 1))
    )
    rez = await db.execute(query)
    return rez.scalars().all()


@cart_router.post("/cart", status_code=201, response_model=CartItemDTO)
async def create_new_cart(db: DBsession, item: CartItemDTO):
    await update_amount(db, item.product_id, -item.amount)
    stmt = insert(CartItem).values(**item.model_dump())
    stmt = stmt.on_conflict_do_update(
        constraint="cart_user_product_pk",
        set_=dict(amount=CartItem.amount + stmt.excluded.amount),
    )
    stmt = stmt.returning(CartItem)
    rez = await db.scalar(stmt)
    await db.commit()
    return rez


@cart_router.patch(
    "/cart/{user_id}/products/{product_id}",
    status_code=204,
)
async def change_product_amount(
    db: DBsession,
    user_id: UUID,
    new_amount: Annotated[int, Body(gt=0, embed=True)],
    product_id: UUID,
    cart_item=Depends(check_user_product_exists),
):
    old_amount = cart_item.amount
    diff = new_amount - old_amount
    await update_amount(db, product_id, -diff)

    cart_item.amount = new_amount

    await db.commit()


@cart_router.delete(
    "/cart/{user_id}/products/{product_id}",
    status_code=204,
)
async def delete_product_from_cart(
    db: DBsession,
    user_id: UUID,
    product_id: UUID,
    cart_item=Depends(check_user_product_exists),
):
    old_amount = cart_item.amount
    await update_amount(db, product_id, old_amount)

    await db.delete(cart_item)

    await db.commit()
