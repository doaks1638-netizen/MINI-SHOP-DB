from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from app.models import Category, Product
from app.database import DBsession
from app.schemas import ProductCreate, ProductPatch, ProductDTO
from sqlalchemy import select, and_, insert, update, or_, desc, func
from uuid import UUID
from app.routes import get_current_admin
from fastapi import Query
from app.routes import page_number
from app.schemas import ProductDTO
from app.filters import PriceFilter, ActiveFilter
from typing import Annotated
from app.media import save_product_image, remove_product_image

admin_product_router = APIRouter(
    prefix="/admin/products", tags=["ADMIN"], dependencies=[Depends(get_current_admin)]
)


@admin_product_router.get("/", response_model=list[ProductDTO])
async def get_all_products(
    db: DBsession,
    page: page_number = 1,
    category_id: Annotated[UUID, Query()] = None,
    search: Annotated[str | None, Query()] = None,
    active_filter: Annotated[ActiveFilter, Query()] = ActiveFilter.all,
    price_filter: Annotated[PriceFilter | None, Query()] = None,
):

    filters = []

    if active_filter != ActiveFilter.all:
        match active_filter:
            case ActiveFilter.active:
                filters.extend([Product.is_active == True, Category.is_active == True])
            case ActiveFilter.inactive:
                filters.append(
                    or_(Product.is_active == False, Category.is_active == False)
                )

    if category_id is not None:
        filters.append(Category.id == category_id)

    rank_col = None
    if search is not None:
        search = search.strip()

        if search:
            ts_query_ru = func.websearch_to_tsquery("russian", search)
            ts_query_en = func.websearch_to_tsquery("english", search)

            ts_query = ts_query_en.op("||")(ts_query_ru)

            filters.append(Product.tsv.op("@@")(ts_query))

            rank_col = func.ts_rank_cd(Product.tsv, ts_query).label("rank")

    order_by_filters = []
    if price_filter is not None:
        match price_filter:
            case PriceFilter.more_expensive:
                order_by_filters.append(desc(Product.price))
            case PriceFilter.cheaper:
                order_by_filters.append(Product.price)

    if rank_col is not None:
        stmt = (
            select(Product, rank_col)
            .join(Category)
            .where(*filters)
            .limit(30)
            .offset(30 * (page - 1))
            .order_by(desc(rank_col), *order_by_filters)
        )
    else:
        stmt = (
            select(Product)
            .join(Category)
            .where(*filters)
            .limit(30)
            .offset(30 * (page - 1))
            .order_by(*order_by_filters)
        )

    rez = await db.execute(stmt)

    if rank_col is not None:
        return [x[0] for x in rez.all()]
    return rez.scalars().all()


@admin_product_router.post("/", response_model=ProductDTO)
async def create_new_product(
    db: DBsession,
    new_product: Annotated[ProductCreate, Depends(ProductCreate.as_form)],
    picture_file: Annotated[UploadFile | None, File] = None,
):
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
    image_url = await save_product_image(picture_file) if picture_file else None

    new_data = new_product.model_dump()
    new_data["image_url"] = image_url

    stmt = insert(Product).values(**new_data)
    stmt = stmt.returning(Product)
    product = await db.scalar(stmt)
    await db.commit()
    await db.refresh(product)
    return product



@admin_product_router.patch("/{product_id}")
async def change_product_info(
    db: DBsession,
    product_id: UUID,
    new_info: Annotated[ProductPatch | None, Depends(ProductPatch.as_form)] = None,
    picture_file: Annotated[UploadFile | None, File] = None,
):
    product = await db.get(Product, product_id)

    if not product:
        raise HTTPException(404, detail="Product not found")

    new_info: dict = (
        new_info.model_dump(exclude_unset=True) if new_info is not None else {}
    )

    if not new_info and picture_file is None:
        raise HTTPException(
            status_code=400, detail="At least one field must be provided for update"
        )

    if new_info.get("category_id"):
        new_info_category = select(Category).where(
            Category.id == new_info["category_id"]
        )
        if not await db.scalar(new_info_category):
            raise HTTPException(status_code=404, detail="Active category not found")

    if picture_file is not None:
        remove_product_image(product.image_url)
        new_info["image_url"] = await save_product_image(picture_file)

    for key, value in new_info.items():
        setattr(product, key, value)

    await db.commit()


@admin_product_router.delete("/{product_id}", status_code=204)
async def delete_product(db: DBsession, product_id: UUID):
    product = await db.get(Product, product_id)
    if not product:
        raise HTTPException(404, detail="Product not found")
    product.is_active = False
    await db.commit()
