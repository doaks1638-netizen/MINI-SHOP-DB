from fastapi import APIRouter, HTTPException, Body, Depends, Query
from sqlalchemy import select, insert
from app.models import Category
from app.database import DBsession
from app.schemas import CategoryDTO, CategoryCreate
from typing import Annotated
from uuid import UUID
from app.routes import get_current_admin
from app.schemas import AdminCategoryDTO
from app.routes import page_number
from app.filters import ActiveFilter

admin_category_router = APIRouter(
    prefix="/admin/categories",
    tags=["ADMIN"],
    dependencies=[Depends(get_current_admin)],
)


@admin_category_router.get("/", response_model=list[AdminCategoryDTO])
async def get_categories(
    db: DBsession,
    page: page_number = 1,
    active_filter: Annotated[ActiveFilter, Query()] = ActiveFilter.all,
):
    stmt = select(Category)

    if active_filter != ActiveFilter.all:
        match active_filter:
            case ActiveFilter.active:
                stmt = stmt.where(Category.is_active == True)
            case ActiveFilter.inactive:
                stmt = stmt.where(Category.is_active == False)

    stmt = stmt.limit(30).offset(30 * (page - 1))

    rez = await db.scalars(stmt)
    return rez.all()


@admin_category_router.post(
    "/",
    status_code=201,
    response_model=CategoryDTO,
)
async def create_category(db: DBsession, new_category: CategoryCreate):
    query = select(1).select_from(Category).where(Category.name == new_category.name)
    category_with_same_name = await db.scalar(query)
    if category_with_same_name:
        raise HTTPException(status_code=409, detail="Category already exist")

    stmt = insert(Category).values(**new_category.model_dump())
    stmt = stmt.returning(Category)
    rez = await db.scalar(stmt)
    await db.commit()
    await db.refresh(rez)
    return rez


@admin_category_router.patch(
    "/{category_id}",
    status_code=200,
)
async def change_category_name(
    db: DBsession,
    category_id: UUID,
    name: Annotated[str, Body(embed=True, max_length=50)],
):
    check = select(Category).where(Category.id == category_id)
    category = await db.scalar(check)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    category.name = name
    await db.commit()
    return None


@admin_category_router.delete(
    "/{category_id}",
    status_code=204,
)
async def delete_category(db: DBsession, category_id: UUID):
    category: Category = await db.scalar(
        select(Category).where(Category.id == category_id)
    )
    if not category:
        raise HTTPException(404, detail="Category not found")
    category.is_active = False
    await db.commit()
