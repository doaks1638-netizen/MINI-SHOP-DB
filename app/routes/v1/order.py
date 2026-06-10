from fastapi import APIRouter, HTTPException
from app.database import DBsession
from sqlalchemy import select, insert, update
from sqlalchemy.orm import selectinload
from app.models.order import Order
from app.models.user import User
from app.models.product import Product
from app.models.order_item import OrderItem
from app.services import update_amount, debit_funds
from app.schemas import OrderDTO, OrderCreateRequest, OrderStatusEdit, OrderRelDTO
from app.models.categories import Category
from uuid import UUID
from app.routes.dependencies import page_number

order_router = APIRouter(tags=["orders"])


@order_router.get(
    "/orders", response_model=list[OrderDTO]
)  # тут вытащить из токена кто это запросил и показть спискок просто заказов без items ему
async def get_all_orders(db: DBsession, page: page_number):
    stmt = (
        select(Order)
        .join(User, User.id == Order.user_id)
        .where(User.is_active == True)
        .limit(30)
        .offset(30 * (page - 1))
    )
    rez = await db.scalars(stmt)
    return [OrderDTO.model_validate(x) for x in rez.all()]


@order_router.post("/orders", status_code=201)
async def create_order(db: DBsession, order: OrderCreateRequest):
    user_stmt = (
        select(User).where(User.is_active == True).where(User.id == order.user_id)
    )
    user = await db.scalar(user_stmt)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not order.items:
        raise HTTPException(status_code=400, detail="The order must contain items!")

    new_order = Order(user_id=user.id)
    db.add(new_order)
    await db.flush()

    products_id = {item.product_id for item in order.items}
    order_objects_stmt = (
        select(Product)
        .join(Category, Product.category_id == Category.id)
        .where(Product.is_active == True)
        .where(Category.is_active == True)
        .where(Product.id.in_(products_id))
    )
    rez = await db.scalars(order_objects_stmt)
    order_objects = rez.all()

    products = {p.id: p for p in order_objects}

    if len(products_id) != len(products):
        raise HTTPException(
            status_code=404, detail="The price of some orders not found"
        )

    insert_data = []
    total_order_price = 0

    for item in order.items:
        db_product = products[item.product_id]

        await update_amount(db, item.product_id, -item.amount)

        actual_price = db_product.price

        data = {
            "order_id": new_order.id,
            "amount": item.amount,
            "product_id": item.product_id,
            "price_for_one": actual_price,
        }

        insert_data.append(data)
        total_order_price += actual_price * item.amount

    await debit_funds(db, order.user_id, -total_order_price)

    insert_stmt = insert(OrderItem).values(insert_data)
    new_order.total_price = total_order_price

    await db.execute(insert_stmt)
    await db.commit()

    return {"order_id": new_order.id, "total_price": total_order_price}


@order_router.get("/orders/{order_id}", response_model=OrderRelDTO)
async def get_order_info(db: DBsession, order_id: UUID):
    stmt = (
        select(Order)
        .options(selectinload(Order.items))
        .join(User, User.id == Order.user_id)
        .where(User.is_active == True)
        .where(Order.id == order_id)
    )
    order = await db.scalar(stmt)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return OrderRelDTO.model_validate(order)


@order_router.patch("/orders/{order_id}")
async def change_order(db: DBsession, new_status: OrderStatusEdit, order_id: UUID):
    stmt = (
        update(Order)
        .where(Order.user_id == User.id)
        .where(Order.id == order_id)
        .where(User.is_active == True)
        .values(status=new_status.status)
        .returning(Order.id)
    )
    post = await db.scalar(stmt)
    if not post:
        raise HTTPException(status_code=404, detail="Order not found")
    await db.commit()


@order_router.delete("/orders/{order_id}", status_code=204)  # update amount + payment
async def delete_order(db: DBsession, order_id: UUID):
    stmt = (
        select(Order)
        .options(selectinload(Order.items))
        .join(User, User.id == Order.user_id)
        .where(User.is_active == True)
        .where(Order.id == order_id)
    )
    order = await db.scalar(stmt)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    for order_item in order.items:
        await update_amount(db, order_item.product_id, order_item.amount)
    await db.delete(order)
    await debit_funds(db, order.user_id, order.total_price)
    await db.commit()
