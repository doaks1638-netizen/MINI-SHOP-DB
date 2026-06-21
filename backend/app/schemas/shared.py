# schemes placed in a separate file to avoid circular imports

from pydantic import BaseModel, ConfigDict, Field
from decimal import Decimal
from uuid import UUID
from typing import Annotated


class ProductShare(BaseModel):
    id: UUID
    category_id: UUID
    name: Annotated[str, Field(max_length=100)]
    price: Annotated[Decimal, Field(ge=0)]
    now_amount: Annotated[int, Field(ge=0)]
    model_config = ConfigDict(from_attributes=True)


