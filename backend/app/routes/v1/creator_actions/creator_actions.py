from fastapi import APIRouter, Depends
from app.routes import get_current_creator

creator_router = APIRouter(
    prefix="/creator", dependencies=[Depends(get_current_creator)], tags=["CREATOR"]
)
