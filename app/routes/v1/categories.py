from fastapi import APIRouter, Query, HTTPException, Body
from sqlalchemy import select, insert
from sqlalchemy.orm import selectinload
from app.database import DBsession
from app.schemas import CategoryDTO, CategoryCreate, CategoryRelDTO
from app.models import Category
from typing import Annotated
from uuid6 import UUID

category_router = APIRouter(tags=['CATEGORIES'])

page_number = Annotated[int, Query(gt=0)]


@category_router.get('/categories', response_model=list[CategoryDTO])
async def get_categories(db: DBsession, page: page_number):
    stmt = select(Category)
    rez = await db.scalars(stmt)
    return [CategoryDTO.model_validate(x) for x in rez.all()]


@category_router.post('/categories', status_code=201, response_model=CategoryDTO)
async def create_category(db: DBsession, new_category: CategoryCreate):
    query = select(1).select_from(Category).where(Category.name == new_category.name)
    category_with_same_name = await db.scalar(query)
    if category_with_same_name:
        raise HTTPException(status_code=409, detail='Category already exist')
    
    stmt = insert(Category).values(**new_category.model_dump())
    stmt = stmt.returning(Category)
    rez = await db.scalar(stmt)
    await db.commit()
    return CategoryDTO.model_validate(rez)


@category_router.get('/categories/{category_id}', response_model=CategoryRelDTO)
async def get_category(db: DBsession, category_id: UUID):
    stmt = select(Category).options(selectinload(Category.products)).where(Category.id == category_id)
    rez = await db.scalar(stmt)
    if not rez:
        raise HTTPException(status_code=404, detail='Category not found')
    return CategoryRelDTO.model_validate(rez)


@category_router.patch('/categories/{category_id}', status_code=204)
async def change_category_name(db: DBsession, category_id: UUID, name: Annotated[str, Body(embed=True, max_length=50)]):
    check = select(Category).where(Category.id == category_id)
    category = await db.scalar(check)
    if not category:
        raise HTTPException(status_code=404, detail='Category is not exist')
    category.name = name
    await db.commit()
    return None
