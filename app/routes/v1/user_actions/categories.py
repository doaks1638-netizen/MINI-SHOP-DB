from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload, with_loader_criteria
from app.database import DBsession
from app.schemas import CategoryDTO, CategoryRelDTO
from app.models.categories import Category
from app.models.product import Product
from uuid import UUID
from app.routes import page_number

category_router = APIRouter(tags=["CATEGORIES"])


@category_router.get("/categories", response_model=list[CategoryDTO])
async def get_categories(db: DBsession, page: page_number):
    stmt = (
        select(Category)
        .where(Category.is_active == True)
        .limit(30)
        .offset(30 * (page - 1))
    )
    rez = await db.scalars(stmt)
    return rez.all()


@category_router.get("/categories/{category_id}", response_model=CategoryRelDTO)
async def get_category(db: DBsession, category_id: UUID):
    stmt = (
        select(Category)
        .where(Category.id == category_id, Category.is_active == True)
        .options(
            selectinload(Category.products),
            # Глобально внутри этого запроса отсекаем неактивные продукты
            with_loader_criteria(Product, Product.is_active == True),
        )
    )
    rez = await db.scalar(stmt)
    if not rez:
        raise HTTPException(status_code=404, detail="Category not found")
    return rez
