from fastapi import APIRouter, Body, Depends, Query
from sqlalchemy import select, case
from sqlalchemy.dialects.postgresql import insert
from app.models.cart_item import CartItem
from app.schemas import CartItemDTO, CartItemWithStatus, CartItemStatus
from app.database import DBsession
from app.services import check_user_product_exists
from typing import Annotated
from uuid import UUID
from app.routes import page_number
from app.models.user import User
from app.models.product import Product
from app.routes import get_current_user

cart_router = APIRouter(tags=["CART"], prefix="/cart")


@cart_router.get("/", response_model=list[CartItemWithStatus])
async def get_user_cart(
    db: DBsession,
    page: page_number,
    user: Annotated[User, Depends(get_current_user)],
    product_id: Annotated[
        UUID, Query()
    ] = None,  # выборка товаров (если в корзине много товаров)
    search: Annotated[str, Query()] = None,
):
    query = (
        select(
            CartItem.user_id,
            CartItem.product_id,
            CartItem.amount,
            case(
                (Product.now_amount >= CartItem.amount, CartItemStatus.in_stock),
                else_=CartItemStatus.out_of_stock,
            ).label("status"),
        )
        .join(User, CartItem.user_id == User.id)
        .join(Product, CartItem.product_id == Product.id)
        .where(User.is_active == True, Product.is_active == True)
        .where(CartItem.user_id == user.id)
        .limit(30)
        .offset(30 * (page - 1))
    )

    if product_id is not None:
        query = query.where(Product.id == product_id)

    if search is not None:
        query = query.where(Product.name.like(f"%{search}%"))

    rez = await db.execute(query)
    return rez.mappings().all()


@cart_router.post("/", status_code=201, response_model=CartItemDTO)
async def create_new_cart(
    db: DBsession, item: CartItemDTO, user: Annotated[User, Depends(get_current_user)]
):
    stmt = insert(CartItem).values(**item.model_dump(), user_id=user.id)
    stmt = stmt.on_conflict_do_update(
        index_elements=["user_id", "product_id"],
        set_=dict(amount=CartItem.amount + stmt.excluded.amount),
    )
    stmt = stmt.returning(CartItem)
    rez = await db.scalar(stmt)
    result_dto = CartItemDTO.model_validate(rez)
    await db.commit()
    return result_dto


@cart_router.patch(
    "/products/{product_id}",
    status_code=204,
)
async def change_product_amount(
    db: DBsession,
    user: Annotated[User, Depends(get_current_user)],
    new_amount: Annotated[int, Body(gt=0, embed=True)],
    product_id: UUID,
):
    cart_item = await check_user_product_exists(db, user.id, product_id)
    cart_item.amount = new_amount

    await db.commit()


@cart_router.delete(
    "/products/{product_id}",
    status_code=204,
)
async def delete_product_from_cart(
    db: DBsession, user: Annotated[User, Depends(get_current_user)], product_id: UUID
):
    cart_item = await check_user_product_exists(db, user.id, product_id)

    await db.delete(cart_item)

    await db.commit()
