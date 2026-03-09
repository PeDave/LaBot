from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.config import settings

app = FastAPI(
    title="LaBot Chart Analyzer",
    description="AI-powered crypto chart technical analysis service",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")


@app.get("/")
async def root() -> dict:
    return {
        "service": "LaBot Chart Analyzer",
        "version": "0.1.0",
        "docs": "/docs",
    }
