from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.product import Product
from app.models.categories import Category


async def update_amount(db: AsyncSession, product_id, diff):
    product = await db.scalar(
        select(Product)
        .join(Category, Product.category_id == Category.id)
        .where(
            Product.id == product_id,
            Category.is_active == True,
            Product.is_active == True,
        )
        .with_for_update(of=Product)  # only block Product table
    )
    if not product:
        raise HTTPException(404, detail="Product not found")
    new_amount = product.now_amount + diff
    if new_amount < 0:
        raise HTTPException(
            status_code=409, detail="Insufficient stock in the warehouse"
        )
    product.now_amount = new_amount
