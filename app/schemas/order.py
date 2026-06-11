from pydantic import BaseModel, ConfigDict
from uuid import UUID
from app.models.order_status_enum import OrderStatus
from app.schemas.shared import OrderItemShare
from datetime import datetime
from decimal import Decimal


class OrderCreate(BaseModel):
    user_id: UUID
    total_price: Decimal


class OrderDTO(OrderCreate):
    id: UUID
    status: OrderStatus
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class OrderStatusEdit(BaseModel):
    status: OrderStatus


class OrderRelDTO(OrderDTO):
    items: list['OrderItemShare']
