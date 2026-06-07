from sqlalchemy.orm import DeclarativeBase, mapped_column
from typing import Annotated
from uuid6 import UUID as UUID7, uuid7
from sqlalchemy import text, UUID as UUID_sql


class Base(DeclarativeBase):
    type_annotation_map = {
        UUID7: UUID_sql
    }


idpk = Annotated[
    UUID7, mapped_column(primary_key=True,default=uuid7, server_default=text('uuidv7()'))
]
