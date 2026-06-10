from fastapi import APIRouter, HTTPException
from app.database import DBsession
from app.routes.dependencies import page_number
from app.models.product import Product
from app.models.categories import Category
from app.schemas import ProductDTO, ProductCreate, ProductRelDTO, ProductPatch
from sqlalchemy import select, and_, insert, update
from sqlalchemy.orm import joinedload
from uuid import UUID

product_router = APIRouter()


@product_router.get("/products", response_model=list[ProductDTO])
async def get_all_products(db: DBsession, page: page_number):
    stmt = (
        select(Product)
        .join(Category)
        .where(Product.is_active == True, Category.is_active == True)
        .limit(30)
        .offset(30 * (page - 1))
    )
    rez = await db.scalars(stmt)
    return [ProductDTO.model_validate(x) for x in rez]


@product_router.post("/products")
async def create_new_product(db: DBsession, new_product: ProductCreate):
    stmt = (
        select(Product)
        .join(Category)
        .where(Product.is_active == True, Category.is_active == True)
        .where(
            and_(
                Product.category_id == new_product.category_id,
                Product.name == new_product.name,
            )
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


@product_router.get("/products/{product_id}", response_model=ProductRelDTO)
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
    return ProductRelDTO.model_validate(product)


@product_router.patch("/products/{product_id}")
async def change_product_info(db: DBsession, new_info: ProductPatch, product_id: UUID):
    new_info = new_info.model_dump(exclude_unset=True)
    if not new_info:
        raise HTTPException(
            status_code=400, detail="At least one field must be provided for update"
        )
    stmt = (
        update(Product)
        .where(Product.category_id == Category.id)
        .where(Product.id == product_id)
        .where(Product.is_active == True, Category.is_active == True)
        .values(**new_info)
        .returning(Product.id)
    )
    new_product = await db.scalar(stmt)
    if not new_product:
        raise HTTPException(status_code=404, detail="Product not found")
    await db.commit()
