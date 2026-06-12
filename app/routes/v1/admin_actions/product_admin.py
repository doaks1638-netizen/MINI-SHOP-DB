from fastapi import APIRouter, HTTPException, Depends
from app.database import DBsession
from app.models.product import Product
from app.models.categories import Category
from app.schemas import ProductCreate, ProductPatch
from sqlalchemy import select, and_, insert, update
from uuid import UUID
from app.routes import get_current_admin

admin_product_router = APIRouter(
    prefix="/admin/products", tags=["ADMIN"], dependencies=[Depends(get_current_admin)]
)


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
            Category.id == new_info["category_id"], Category.is_active == True
        )
        if not await db.scalar(new_info_category):
            raise HTTPException(status_code=404, detail="Active category not found")
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


@admin_product_router.delete("/{product_id}", status_code=204)
async def delete_product(db: DBsession, product_id: UUID):
    product = await db.scalar(
        select(Product).where(Product.id == product_id, Product.is_active == True)
    )
    if not product:
        raise HTTPException(404, detail="Product not found")
    product.is_active = False
    await db.commit()
