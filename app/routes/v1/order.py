from fastapi import APIRouter, Query
from app.database import DBsession
from sqlalchemy.sql import select
from app.models import Order
from typing import Annotated
from app.schemas import CategoryDTO, OrderCreate

post_router = APIRouter(tags="posts")

page_number = Annotated[int, Query(gt=0)]


@post_router.get("/orders", response_model=list[CategoryDTO])
async def get_all_orders(db: DBsession, page: page_number):
    stmt = select(Order).limit(30).offset(30 * (page - 1))
    rez = await db.scalars(stmt)
    return [CategoryDTO.model_validate(x) for x in rez.all()]


# @post_router.post('orders', status_code=204)
