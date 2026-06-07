from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.product import Product


async def update_amount(db: AsyncSession, product_id, diff):
    product = await db.get(Product, product_id)
    new_amount = product.now_amount + diff
    if new_amount < 0:
        raise HTTPException(
            status_code=409, detail="Insufficient stock in the warehouse"
        )
    product.now_amount = new_amount
