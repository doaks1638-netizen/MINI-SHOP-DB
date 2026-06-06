from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from typing import Annotated

class Cart(BaseModel):
    user_id:UUID
    total_products:int
    total_items:int

class CartItemDTO(BaseModel):
    product_id: UUID
    amount: Annotated[int, Field(gt=0)]
    model_config = ConfigDict(from_attributes=True)



