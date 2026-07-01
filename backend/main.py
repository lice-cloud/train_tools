import os
import sys
import threading
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

from backend.updater import check_update, start_download, get_download_status, apply_update


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


@app.get("/api/check-update")
async def check_update_endpoint():
    result = check_update()
    return result


class UpdateRequest(BaseModel):
    download_url: str


@app.post("/api/update")
async def update(req: UpdateRequest):
    start_download(req.download_url)
    return {"status": "started"}


@app.get("/api/update-status")
async def update_status():
    return get_download_status()


@app.post("/api/update-apply")
async def update_apply():
    threading.Thread(target=apply_update, daemon=False).start()
    return {"status": "applying"}
