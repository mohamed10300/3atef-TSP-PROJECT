from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings

_BASE_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000"]


def apply_middleware(app: FastAPI) -> None:
    extra = [o.strip() for o in settings.ALLOWED_ORIGINS.split(",") if o.strip()]
    origins = list({settings.FRONTEND_URL, *_BASE_ORIGINS, *extra})
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
