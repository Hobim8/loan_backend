from fastapi import FastAPI, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from core.auth import auth_router
from routes.loan import loan_route
from routes.monitoring import monitoring_route

app = FastAPI(
    title="Loan Backend",
    description="Loan risk prediction API with model monitoring",
    version="0.1.0",
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
