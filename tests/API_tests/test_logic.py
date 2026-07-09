from app.models import Product, Category
import pytest
from uuid6 import uuid7
from asyncio import TaskGroup

# If it seems to you that my test architecture in this file is overly cumbersome—well,
#  you aren't imagining things. Each test generates and validates its own distinct data.
# Why not just do it once in a fixture? Let's consider how we might solve this. We create
# a single fixture with `scope='module'` and... Everything breaks because of the `pytest-asyncio` plugin.
# That is precisely why I opted for this approach.
# If you now how to fix it -> doaks1638@gmail.com, telegram: @ooopev


@pytest.fixture(scope="function")
async def category_saver(db):
    async def category_saver_interior(name: str = None):
        if name is None:
            name = f"{uuid7()}"
        category = Category(name=name)
        db.add(category)
        await db.commit()
        await db.refresh(category)
        return category.id

    return category_saver_interior


@pytest.fixture(scope="function")
async def product_saver(db):
    async def product_saver_interior(
        category_id: int, name: str, price: int, now_amount: int, description: str
    ):
        product = Product(
            category_id=category_id,
            name=name,
            price=price,
            now_amount=now_amount,
            description=description,
        )
        db.add(product)
        await db.commit()
        await db.refresh(product)
        return product

    return product_saver_interior


class TestSorting:
    async def test_FTSearch(self, auth_client, category_saver, product_saver):
        id, auth_client = auth_client
        category_id = await category_saver()
        # test 2 products for search
        await product_saver(
            category_id=category_id,
            name="LG phone 17 pro MAX",
            price=1000,
            now_amount=100,
            description="test",
        )
        await product_saver(
            category_id=category_id,
            name='LG Телевизор 65NANO80A6B 65" 4K UHD, черный',
            price=1000,
            now_amount=100,
            description="test",
        )
        responce = (await auth_client.get("/api/v1/products/?page=1&search=LG Телевизоры")).json() # default serach
        assert len(responce) == 1
        assert responce[0]["name"] == 'LG Телевизор 65NANO80A6B 65" 4K UHD, черный'
        responce = (
            await auth_client.get("/api/v1/products/?page=1&search=test") # search by description
        ).json()
        assert len(responce) == 2
        assert responce[0]["name"] in (
            'LG Телевизор 65NANO80A6B 65" 4K UHD, черный',
            "LG phone 17 pro MAX",
        )

        assert responce[1]["name"] in (
            'LG Телевизор 65NANO80A6B 65" 4K UHD, черный',
            "LG phone 17 pro MAX",
        )
        responce = (
            await auth_client.get("/api/v1/products/?page=1&search=LG -phone") 
        ).json()
        assert len(responce) == 1
        assert responce[0]["name"] == 'LG Телевизор 65NANO80A6B 65" 4K UHD, черный'

    async def test_query_params(self): ...
