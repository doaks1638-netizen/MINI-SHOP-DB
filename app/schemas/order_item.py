from pydantic import BaseModel, Field
from uuid import UUID
from decimal import Decimal
from typing import Annotated


class OrderItemCreate(BaseModel):
    product_id: UUID
    amount: Annotated[int, Field(gt=0)]


class OrderItemDTO(OrderItemCreate):
    order_id: UUID
    price_for_one: Annotated[Decimal, Field(ge=0)]


class OrderCreateRequest(BaseModel):
    user_id: UUID
    items: list["OrderItemCreate"]
