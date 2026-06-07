from fastapi import APIRouter, Query, Body, Depends, HTTPException
from sqlalchemy import select, func, and_, update, delete
from sqlalchemy.dialects.postgresql import insert
from app.models.cart_item import CartItem
from app.models.product import Product
from app.schemas import Cart, CartItemDTO
from app.database import DBsession
from app.services import check_user_product_exists, update_amount
from typing import Annotated
from uuid import UUID
from app.routes.dependencies import page_number

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
        .group_by(CartItem.user_id)
        .limit(30)
        .offset(30 * (page - 1))
    )
    rez = await db.execute(query)
    return [Cart.model_validate(x) for x in rez.mappings().all()]


@cart_router.get("/cart/{user_id}", response_model=list[CartItemDTO])
async def get_user_cart(db: DBsession, page: page_number, user_id: UUID):
    query = (
        select(CartItem)
        .where(CartItem.user_id == user_id)
        .limit(30)
        .offset(30 * (page - 1))
    )
    rez = await db.execute(query)
    return [CartItemDTO.model_validate(x) for x in rez.scalars().all()]


@cart_router.post("/cart", status_code=201)
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
    return CartItemDTO.model_validate(rez)


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

    db.delete(cart_item)

    await db.commit()
