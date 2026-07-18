from pathlib import Path

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from core.auth import auth_router
from routes.loan import loan_route
from routes.monitoring import monitoring_route

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

app = FastAPI(
    title="Loan Backend",
    description="Loan risk prediction API with model monitoring",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8000",
        "http://localhost:8000",
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(loan_route)
app.include_router(monitoring_route)


@app.get("/metrics")
def prometheus_metrics():
    """
    Prometheus scrape endpoint.

    Intended for internal scrapers (network-restrict in production).
    JSON monitoring analytics remain staff-only under /monitoring/*.
    """
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def frontend_index():
    """Serve the Apex Underwriting UI."""
    index = FRONTEND_DIR / "index.html"
    if not index.is_file():
        return {"message": "Frontend not found. Expected frontend/index.html"}
    return FileResponse(index)


if FRONTEND_DIR.is_dir():
    app.mount(
        "/assets",
        StaticFiles(directory=FRONTEND_DIR / "assets"),
        name="frontend-assets",
    )
