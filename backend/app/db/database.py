from app.core.settings import settings
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from fastapi import Depends
from typing import Annotated, AsyncGenerator

engine = create_async_engine(
    url=settings.get_db_url(),
    echo=settings.db.DEBUG,
    pool_size=10,
    max_overflow=20,
)

SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session


type DBsession = Annotated[AsyncSession, Depends(get_db)]
