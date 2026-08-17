from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from . import config
from .pipeline.orchestrator import enrich_company
from .storage import ResultStore

app = FastAPI(title="Company Insight Enrichment API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

store = ResultStore(config.DATA_FILE)


class EnrichRequest(BaseModel):
    url: str
    website_name: str = ""


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/enrich")
def enrich(payload: EnrichRequest) -> dict:
    if not payload.url or not payload.url.strip():
        raise HTTPException(status_code=422, detail="url is required")

    profile = enrich_company(payload.url, label=payload.website_name)
    store.upsert(profile)
    return profile


@app.get("/results")
def results() -> list[dict]:
    return store.all()


frontend_dir = Path(__file__).resolve().parent.parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")
