import pytest
from uuid6 import uuid7
from asyncio import TaskGroup

# If it seems to you that my test architecture in this file is overly cumbersome—well,
#  you aren't imagining things. Each test generates and validates its own distinct data.
# Why not just do it once in a fixture? Let's consider how we might solve this. We create
# a single fixture with `scope='module'` and... Everything breaks because of the `pytest-asyncio` plugin.
# That is precisely why I opted for this approach.
# If you now how to fix it -> doaks1638@gmail.com, telegram: @ooopev


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
        response = (
            await auth_client.get(
                "/api/v1/products/", params={"search": "TEST LG Телевизоры", "category_id": f"{category_id}"}
            )
        ).json()  # default serach
        assert len(response) == 1
        assert response[0]["name"] == 'TEST LG Телевизор 65NANO80A6B 65" 4K UHD, черный'
        response = (
            await auth_client.get(
                "/api/v1/products/", params={"search": "test", "category_id": f"{category_id}"}
            )  # search by description
        ).json()
        assert len(response) == 2
        assert response[0]["name"] in (
            'TEST LG Телевизор 65NANO80A6B 65" 4K UHD, черный',
            "TEST LG phone 17 pro MAX",
        )

        assert response[1]["name"] in (
            'TEST LG Телевизор 65NANO80A6B 65" 4K UHD, черный',
            "TEST LG phone 17 pro MAX",
        )
        response = (
            await auth_client.get(
                "/api/v1/products/",
                params={"search": "LG -phone", "category_id": f"{category_id}"},
            )
        ).json()
        assert len(response) == 1
        assert response[0]["name"] == 'TEST LG Телевизор 65NANO80A6B 65" 4K UHD, черный'

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
        response = (
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
            sorted(response, key=lambda x: float(x["price"]), reverse=True) == response
        )
        for product in response:
            assert product["category_id"] == str(category_id)
