# auntification function for future
from fastapi import Depends

async def get_current_user():
    # just return user (jwt)
    pass

async def get_current_admin(current_user = Depends(get_current_user)):
    # if user is not admin - raise HTTPexception
    return current_user