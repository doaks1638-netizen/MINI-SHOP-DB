from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.v1 import v1_router
from fastapi.staticfiles import StaticFiles
from app.core.settings import settings
import mimetypes
from app.core.limiter import limiter
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded


mimetypes.add_type("image/webp", ".webp")

app = FastAPI(title="MINI-SHOP-DB")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(v1_router)

app.mount("/media", StaticFiles(directory=str(settings.BASE_DIR / "media")), name="media")
