from fastapi import APIRouter, Query
from sqlalchemy import select, func
from app.models import CartItem
from app.schemas import Cart, CartItemDTO
from app.database import DBsession
from typing import Annotated
from uuid import UUID

cart_router = APIRouter()

page_number = Annotated[int, Query(gt=0)]


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
