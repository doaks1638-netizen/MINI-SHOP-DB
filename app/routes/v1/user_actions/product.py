from fastapi import APIRouter, HTTPException, Query
from app.models import Category, Product
from app.database import DBsession
from app.routes import page_number
from app.schemas import ProductDTO, ProductRelDTO
from sqlalchemy import select, desc
from sqlalchemy.orm import joinedload
from uuid import UUID
from typing import Annotated
from app.filters import PriceFilter

product_router = APIRouter(prefix="/products", tags=["PRODUCTS"])


@product_router.get("/", response_model=list[ProductDTO])
async def get_all_products(
    db: DBsession,
    page: page_number,
    category_id: Annotated[UUID | None, Query()] = None,
    search: Annotated[str | None, Query()] = None,
    price_filter: Annotated[PriceFilter | None, Query()] = None,
):
    stmt = (
        select(Product)
        .join(Category)
        .where(Product.is_active == True, Category.is_active == True)
    )

    if category_id is not None:
        stmt = stmt.where(Category.id == category_id)

    if search is not None:
        stmt = stmt.where(Product.name.ilike(f"%{search}%"))

    if price_filter is not None:
        match price_filter:
            case PriceFilter.more_expensive:
                stmt = stmt.order_by(desc(Product.price))
            case PriceFilter.cheaper:
                stmt = stmt.order_by(Product.price)

    stmt = stmt.limit(30).offset(30 * (page - 1))

    rez = await db.scalars(stmt)
    return rez.all()


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
