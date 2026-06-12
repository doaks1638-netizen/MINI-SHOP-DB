from fastapi import APIRouter, HTTPException, Query
from app.database import DBsession
from app.routes import page_number
from app.models.product import Product
from app.models.categories import Category
from app.schemas import ProductDTO, ProductRelDTO
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from uuid import UUID
from typing import Annotated

product_router = APIRouter(prefix="/products", tags=["PRODUCTS"])


@product_router.get("/", response_model=list[ProductDTO])
async def get_all_products(
    db: DBsession,
    page: page_number,
    category_id: Annotated[UUID, Query()] = None,
    search: Annotated[str, Query()] = None,
):
    stmt = (
        select(Product)
        .join(Category)
        .where(Product.is_active == True, Category.is_active == True)
        .limit(30)
        .offset(30 * (page - 1))
    )
    if category_id is not None:
        stmt = stmt.where(Category.id == category_id)

    if search is not None:
        stmt = stmt.where(Category.name.like(f"%{search}%"))

    rez = await db.scalars(stmt)
    return rez


@product_router.get("/{product_id}", response_model=ProductRelDTO)
async def get_product(db: DBsession, product_id: UUID):
    stmt = (
        select(Product)
        .join(Category)
        .where(Product.is_active == True, Category.is_active == True)
        .options(joinedload(Product.category))
        .where(Product.id == product_id)
    )
    product = await db.scalar(stmt)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
