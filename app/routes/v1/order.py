from fastapi import APIRouter, Query, HTTPException
from app.database import DBsession
from sqlalchemy import select, insert, update, delete
from app.models.order import Order
from app.models.user import User
from app.models.product import Product
from app.models.order_item import OrderItem
from typing import Annotated
from app.schemas import OrderDTO, OrderCreateRequest, OrderStatusEdit
from uuid6 import UUID

post_router = APIRouter(tags="posts")

page_number = Annotated[int, Query(gt=0)]


@post_router.get("/orders", response_model=list[OrderDTO])
async def get_all_orders(db: DBsession, page: page_number):
    stmt = select(Order).limit(30).offset(30 * (page - 1))
    rez = await db.scalars(stmt)
    return [OrderDTO.model_validate(x) for x in rez.all()]


@post_router.post("/orders", status_code=201)
async def create_order(db: DBsession, order: OrderCreateRequest):
    user_stmt = select(User).where(User.id == order.user_id)
    user = await db.scalar(user_stmt)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not order.items:
        raise HTTPException(status_code=400, detail="The order must contain items!")

    new_order = Order(user_id=user.id)
    db.add(new_order)
    await db.flush()

    products_id = {item.product_id for item in order.items}
    order_objects_stmt = select(Product).where(Product.id.in_(products_id))
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

        actual_price = db_product.price

        data = {
            "order_id": new_order.id,
            "amount": item.amount,
            "product_id": item.product_id,
            "price_for_one": actual_price,
        }

        insert_data.append(data)
        total_order_price += actual_price * item.amount

    insert_stmt = insert(OrderItem).values(insert_data)
    new_order.total_price = total_order_price

    await db.execute(insert_stmt)
    await db.commit()

    return {"order_id": new_order.id, "total_price": total_order_price}


@post_router.get("/orders/{order_id}", response_model=OrderDTO)
async def get_order_info(db: DBsession, order_id: UUID):
    stmt = select(Order).where(Order.id == order_id)
    order = await db.scalar(stmt)
    return OrderDTO.model_validate(order)


@post_router.patch("/orders/{order_id}", status_code=201)
async def change_order(db: DBsession, new_status: OrderStatusEdit, order_id:UUID):
    stmt = update(Order).values(status=new_status.status).where(Order.id == order_id).returning(Order)
    post = await db.scalar(stmt)
    if not post:
        raise HTTPException(status_code=404, detail="Order not found")
    await db.commit()


@post_router.delete("/orders/{order_id}", status_code=204)
async def delete_order(db: DBsession, order_id: UUID):
    stmt = delete(Order).where(Order.id == order_id).returning(Order)
    post = await db.scalar(stmt)
    if not post:
        raise HTTPException(status_code=404, detail="Order not found")
    await db.commit()
