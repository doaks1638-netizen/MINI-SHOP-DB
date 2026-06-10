from fastapi import APIRouter, HTTPException, Body
from sqlalchemy import select, insert
from sqlalchemy.orm import selectinload, with_loader_criteria
from app.database import DBsession
from app.schemas import CategoryDTO, CategoryCreate, CategoryRelDTO
from app.models.categories import Category
from app.models.product import Product
from typing import Annotated
from uuid import UUID
from app.routes.dependencies import page_number

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
    return [CategoryDTO.model_validate(x) for x in rez.all()]


@category_router.post("/categories", status_code=201, response_model=CategoryDTO)
async def create_category(db: DBsession, new_category: CategoryCreate):
    query = (
        select(1)
        .select_from(Category)
        .where(Category.name == new_category.name)
        .where(Category.is_active == True)
    )
    category_with_same_name = await db.scalar(query)
    if category_with_same_name:
        raise HTTPException(status_code=409, detail="Category already exist")

    stmt = insert(Category).values(**new_category.model_dump())
    stmt = stmt.returning(Category)
    rez = await db.scalar(stmt)
    await db.commit()
    return CategoryDTO.model_validate(rez)


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
    return CategoryRelDTO.model_validate(rez)


@category_router.patch("/categories/{category_id}", status_code=204)
async def change_category_name(
    db: DBsession,
    category_id: UUID,
    name: Annotated[str, Body(embed=True, max_length=50)],
):
    check = (
        select(Category)
        .where(Category.id == category_id)
        .where(Category.is_active == True)
    )
    category = await db.scalar(check)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    category.name = name
    await db.commit()
    return None
