import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import select, String, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from pydantic import BaseModel

class Base(DeclarativeBase): pass
class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

class UserDTO(BaseModel):
    id: int
    name: str

async def main():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSession(engine) as db:
        db.add(User(name="test"))
        await db.commit()
        
        stmt = select(User)
        rez = await db.scalars(stmt)
        # simulate FastAPI TypeAdapter validation
        from pydantic import TypeAdapter
        try:
            adapter = TypeAdapter(list[UserDTO])
            print("Adapter can validate?", adapter.validate_python(rez))
        except Exception as e:
            print("Pydantic Error:", e)
            
if __name__ == "__main__":
    asyncio.run(main())
