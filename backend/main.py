import os
import sys
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn


def _frontend_dist() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / "frontend" / "dist"
    if os.environ.get("ENV") == "dev":
        return Path()
    return Path(__file__).resolve().parent.parent / "frontend" / "dist"


@asynccontextmanager
async def lifespan(app: FastAPI):
    dist = _frontend_dist()
    if dist != Path() and dist.exists():
        app.mount("/", StaticFiles(directory=str(dist), html=True), name="frontend")
    yield


app = FastAPI(title="Train Tools", lifespan=lifespan)


@app.get("/api/health")
async def health():
    return {"status": "ok"}
