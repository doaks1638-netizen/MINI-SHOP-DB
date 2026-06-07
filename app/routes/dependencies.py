# auntification function for future
from fastapi import Depends, Query
from typing import Annotated

page_number = Annotated[int, Query(gt=0)]


async def get_current_user():
    # just return user (jwt)
    pass


async def get_current_admin(current_user=Depends(get_current_user)):
    # if user is not admin - raise HTTPexception
    return current_user
