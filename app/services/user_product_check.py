from sqlalchemy.sql import select, and_
from fastapi import HTTPException
from app.database import DBsession
from app.models.cart_item import CartItem
from app.models.user import User
from app.models.product import Product
from uuid import UUID


async def check_user_product_exists(db: DBsession, user_id: UUID, product_id: UUID):
    check = (
        select(CartItem)
        .join(User, CartItem.user_id == User.id)
        .join(Product, CartItem.product_id == Product.id)
        .where(
            CartItem.user_id == user_id,
            CartItem.product_id == product_id,
            User.is_active == True,
            Product.is_active == True,
        ).with_for_update(of=CartItem) # block cartitem (race condition when diff counting with same data)
    )
    rez = await db.scalar(check)
    if not rez:
        raise HTTPException(status_code=404, detail="Product not found in user cart")
    return rez
