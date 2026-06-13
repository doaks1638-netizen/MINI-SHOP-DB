from fastapi import HTTPException
from app.models import Order, Product
from app.database import DBsession
from sqlalchemy import select
from app.services import debit_funds, update_amount
from app.schemas import OrderCreate
from uuid import UUID


async def create_order(
    db: DBsession, order: OrderCreate, user_id: UUID, skip_if_not_in_stock: bool = False
):

    product = await db.scalar(
        select(Product).where(Product.id == order.product_id, Product.is_active == True)
    )

    if not product:
        if skip_if_not_in_stock:
            return None
        raise HTTPException(404, detail="Product not found")

    actual_price = product.price

    new_order = Order(user_id=user_id, price_for_one=actual_price, **order.model_dump())
    db.add(new_order)

    await update_amount(db, order.product_id, -order.amount)

    await debit_funds(db, user_id, -(actual_price * order.amount))

    await db.flush()

    return new_order
