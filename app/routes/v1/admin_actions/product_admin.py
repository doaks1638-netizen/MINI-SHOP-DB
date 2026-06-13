from fastapi import APIRouter, HTTPException, Depends
from app.models import Category, Product
from app.database import DBsession
from app.schemas import ProductCreate, ProductPatch
from sqlalchemy import select, and_, insert, update, or_, desc
from uuid import UUID
from app.routes import get_current_admin
from fastapi import Query
from app.routes import page_number
from app.schemas import ProductDTO
from app.filters import PriceFilter, ActiveFilter
from typing import Annotated


admin_product_router = APIRouter(
    prefix="/admin/products", tags=["ADMIN"], dependencies=[Depends(get_current_admin)]
)


@admin_product_router.get("/", response_model=list[ProductDTO])
async def get_all_products(
    db: DBsession,
    page: page_number,
    category_id: Annotated[UUID, Query()] = None,
    search: Annotated[str | None, Query()] = None,
    active_filter: Annotated[ActiveFilter, Query()] = ActiveFilter.all,
    price_filter: Annotated[PriceFilter | None, Query()] = None,
):
    stmt = select(Product).join(Category)

    if active_filter != ActiveFilter.all:
        match active_filter:
            case ActiveFilter.active:
                stmt = stmt.where(Product.is_active == True, Category.is_active == True)
            case ActiveFilter.inactive:
                stmt = stmt.where(
                    or_(Product.is_active == False, Category.is_active == False)
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


@admin_product_router.post("/")
async def create_new_product(db: DBsession, new_product: ProductCreate):
    stmt = select(Product).where(
        and_(
            Product.category_id == new_product.category_id,
            Product.name == new_product.name,
        )
    )
    same_product = await db.scalar(stmt)
    if same_product:
        raise HTTPException(
            status_code=409,
            detail="Product with same name and category already exists!",
        )
    stmt = insert(Product).values(**new_product.model_dump())
    await db.execute(stmt)
    await db.commit()


@admin_product_router.patch("/{product_id}")
async def change_product_info(db: DBsession, new_info: ProductPatch, product_id: UUID):
    new_info = new_info.model_dump(exclude_unset=True)
    if not new_info:
        raise HTTPException(
            status_code=400, detail="At least one field must be provided for update"
        )
    if new_info.get("category_id"):
        new_info_category = select(Category).where(
            Category.id == new_info["category_id"]
        )
        if not await db.scalar(new_info_category):
            raise HTTPException(status_code=404, detail="Active category not found")
    stmt = (
        update(Product)
        .where(Product.id == product_id)
        .values(**new_info)
        .returning(Product.id)
    )
    new_product = await db.scalar(stmt)
    if not new_product:
        raise HTTPException(status_code=404, detail="Product not found")
    await db.commit()


@admin_product_router.delete("/{product_id}", status_code=204)
async def delete_product(db: DBsession, product_id: UUID):
    product = await db.scalar(select(Product).where(Product.id == product_id))
    if not product:
        raise HTTPException(404, detail="Product not found")
    product.is_active = False
    await db.commit()
