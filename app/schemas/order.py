from pydantic import BaseModel, ConfigDict
from uuid import UUID
from app.schemas.shared import UserShare
from app.models.order_status_enum import OrderStatus
from datetime import datetime


class OrderCreate(BaseModel):
    user_id: UUID
    created_at: datetime
    status: OrderStatus


class OrderDTO(OrderCreate):
    id: UUID

    model_config = ConfigDict(from_attributes=True)


class OrderRelDTO(OrderDTO):
    user: UserShare
