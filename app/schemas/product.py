from pydantic import BaseModel, Field, ConfigDict
from typing import Annotated
from uuid import UUID
from decimal import Decimal
from app.schemas.categories import CategoryDTO
from fastapi import Form


class ProductCreate(BaseModel):
    category_id: UUID
    name: Annotated[str, Field(max_length=100)]
    description: Annotated[str | None, Field(max_length=200)] = None
    price: Annotated[Decimal, Field(ge=0)]
    now_amount: Annotated[int, Field(ge=0)]
    is_active: bool
    image_url: str | None = None

    @classmethod
    def as_form(
        cls,
        category_id: Annotated[UUID, Form()],
        name: Annotated[str, Form()],
        price: Annotated[Decimal, Form()],
        now_amount: Annotated[int, Form()],
        is_active: Annotated[bool, Form()],
        description: Annotated[str | None, Form()] = None,
    ):
        return cls(
            category_id=category_id,
            name=name,
            price=price,
            now_amount=now_amount,
            is_active=is_active,
            description=description,
        )


class ProductDTO(ProductCreate):
    id: UUID
    model_config = ConfigDict(from_attributes=True)


class ProductRelDTO(ProductDTO):
    category: CategoryDTO


class ProductPatch(BaseModel):
    category_id: UUID | None = None
    name: Annotated[str | None, Field(max_length=100)] = None
    description: Annotated[str | None, Field(max_length=200)] = None
    price: Annotated[Decimal | None, Field(ge=0)] = None
    now_amount: Annotated[int | None, Field(ge=0)] = None
    is_active: bool = True

    @classmethod
    def as_form(
        cls,
        category_id: Annotated[UUID | None, Form()] = None,
        name: Annotated[str | None, Form()] = None,
        description: Annotated[str | None, Form()] = None,
        price: Annotated[Decimal | None, Form()] = None,
        now_amount: Annotated[int | None, Form()] = None,
        is_active: Annotated[bool | None, Form()] = None,
    ):
        return cls(
            category_id=category_id,
            name=name,
            description=description,
            price=price,
            now_amount=now_amount,
            is_active=is_active,
        )
