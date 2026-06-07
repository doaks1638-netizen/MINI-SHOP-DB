from pydantic import BaseModel, ConfigDict, Field
from uuid6 import UUID
from typing import Annotated
from app.schemas.shared import ProductShare


class CategoryCreate(BaseModel):
    name: Annotated[str, Field(max_length=50)]


class CategoryDTO(CategoryCreate):
    id: UUID
    model_config = ConfigDict(from_attributes=True)


class CategoryRelDTO(CategoryDTO):
    products: list[ProductShare] = []
