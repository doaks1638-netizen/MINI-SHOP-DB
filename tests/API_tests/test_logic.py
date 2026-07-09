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
        category_id = await category_saver(name="test_FTSearch")
        # test 2 products for search
        await product_saver(
            category_id=category_id,
            name="TEST LG phone 17 pro MAX",
            price=1000,
            now_amount=100,
            description="test",
        )
        await product_saver(
            category_id=category_id,
            name='TEST LG Телевизор 65NANO80A6B 65" 4K UHD, черный',
            price=1000,
            now_amount=100,
            description="test",
        )
        responce = (
            await auth_client.get(
                "/api/v1/products/", params={"search": "TEST LG Телевизоры"}
            )
        ).json()  # default serach
        assert len(responce) == 1
        assert responce[0]["name"] == 'TEST LG Телевизор 65NANO80A6B 65" 4K UHD, черный'
        responce = (
            await auth_client.get(
                "/api/v1/products/", params={"search": "test"}
            )  # search by description
        ).json()
        assert len(responce) == 2
        assert responce[0]["name"] in (
            'TEST LG Телевизор 65NANO80A6B 65" 4K UHD, черный',
            "TEST LG phone 17 pro MAX",
        )

        assert responce[1]["name"] in (
            'TEST LG Телевизор 65NANO80A6B 65" 4K UHD, черный',
            "TEST LG phone 17 pro MAX",
        )
        responce = (
            await auth_client.get("/api/v1/products/", params={"search": "LG -phone"})
        ).json()
        assert len(responce) == 1
        assert responce[0]["name"] == 'TEST LG Телевизор 65NANO80A6B 65" 4K UHD, черный'

    async def test_query_params(self, auth_client, category_saver, product_saver):
        id, auth_client = auth_client
        category_id = await category_saver(name="test_query_params")
        await product_saver(
            category_id=category_id,
            name='TEST Samsung Телевизор 55QE55Q60AAU 55" 4K QLED, серый',
            price=850,
            now_amount=45,
            description="QLED экран, поддержка HDR10+, Smart TV на базе Tizen.",
        )

        await product_saver(
            category_id=category_id,
            name="TEST Apple Смартфон iPhone 15 128GB, черный",
            price=900,
            now_amount=120,
            description="Дисплей Super Retina XDR, чип A16 Bionic, основная камера 48 Мп.",
        )

        await product_saver(
            category_id=category_id,
            name='TEST ASUS Ноутбук Vivobook 15 X1504ZA-BQ102 15.6", синий',
            price=650,
            now_amount=30,
            description="Intel Core i5, 16GB RAM, 512GB SSD, IPS-матрица.",
        )
        responce = (
            await auth_client.get(
                "/api/v1/products/",
                params={
                    "search": "TEST",
                    "price_filter": "more_expensive",
                    "category_id": f"{category_id}",
                },
            )
        ).json()
        assert (
            sorted(responce, key=lambda x: float(x["price"]), reverse=True) == responce
        )
        for product in responce:
            assert product["category_id"] == str(category_id)
