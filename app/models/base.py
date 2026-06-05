from sqlalchemy.orm import DeclarativeBase, mapped_column
from typing import Annotated
from uuid import UUID
from sqlalchemy import text


class Base(DeclarativeBase):
    pass


idpk = Annotated[
    UUID, mapped_column(primary_key=True, server_default=text("gen_random_uuid()"))
]
