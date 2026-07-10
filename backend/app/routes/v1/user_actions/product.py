from fastapi import APIRouter, HTTPException, Query
from app.models import Category, Product
from backend.app.db.database import DBsession
from app.routes import page_number
from app.schemas import ProductDTO, ProductRelDTO
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload
from uuid import UUID
from typing import Annotated
from app.filters import PriceFilter

product_router = APIRouter(prefix="/products", tags=["PRODUCTS"])


@product_router.get("/", response_model=list[ProductDTO])
async def get_all_products(
    db: DBsession,
    page: page_number = 1,
    category_id: Annotated[UUID | None, Query()] = None,
    search: Annotated[str | None, Query()] = None,
    price_filter: Annotated[PriceFilter | None, Query()] = None,
):

    filters = []
    orders_filter = []

    if category_id is not None:
        filters.append(Category.id == category_id)

    if price_filter is not None:
        match price_filter:
            case PriceFilter.more_expensive:
                orders_filter.append(Product.price.desc())
            case PriceFilter.cheaper:
                orders_filter.append(Product.price)

    rank_col = None
    if search is not None:
        search = search.strip()

        if search:
            ts_query_ru = func.websearch_to_tsquery("russian", search)
            ts_query_en = func.websearch_to_tsquery("english", search)

            ts_query = ts_query_en.op("||")(ts_query_ru)

            filters.append(Product.tsv.op("@@")(ts_query))

            rank_col = func.ts_rank_cd(Product.tsv, ts_query).label("rank")

    if rank_col is not None:
        stmt = (
            select(Product, rank_col)
            .join(Category)
            .where(Product.is_active == True, Category.is_active == True)
            .where(*filters)
            .limit(30)
            .offset(30 * (page - 1))
            .order_by(rank_col.desc(), *orders_filter)
        )
    else:
        stmt = (
            select(Product)
            .join(Category)
            .where(Product.is_active == True, Category.is_active == True)
            .where(*filters)
            .limit(30)
            .offset(30 * (page - 1))
            .order_by(*orders_filter)
        )

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
