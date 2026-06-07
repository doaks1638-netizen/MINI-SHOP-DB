from sqlalchemy.sql import select, and_
from fastapi import HTTPException
from app.database import DBsession
from app.models.cart_item import CartItem
from uuid import UUID


async def check_user_product_exists(db: DBsession, user_id: UUID, product_id: UUID):
    check = select(CartItem).where(
        and_(CartItem.user_id == user_id, CartItem.product_id == product_id)
    )
    rez = await db.scalar(check)
    if not rez:
        raise HTTPException(status_code=404, detail="Product not found in user cart")
    return rez
