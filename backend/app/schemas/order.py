from pydantic import BaseModel, ConfigDict
from uuid import UUID
from app.models.enums import OrderStatus, UserStatus
from datetime import datetime
from app.schemas.shared import ProductShare


class OrderCreate(BaseModel):
    product_id: UUID
    amount: int


class OrderDTO(OrderCreate):
    id: UUID
    status: OrderStatus
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class AdminOrderDTO(OrderDTO):
    user_status: UserStatus


class OrderStatusEdit(BaseModel):
    status: OrderStatus


class OrderPatch(BaseModel):
    amount: int


class OrderRelDTO(OrderDTO):
    product: ProductShare
