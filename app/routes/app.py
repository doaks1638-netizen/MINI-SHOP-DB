from fastapi import FastAPI
from app.routes.v1 import v1_router

app = FastAPI(title="MINI-SHOP-DB")

app.include_router(v1_router)
