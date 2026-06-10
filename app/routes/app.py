from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.v1 import v1_router

app = FastAPI(title="MINI-SHOP-DB")

app.include_router(v1_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
