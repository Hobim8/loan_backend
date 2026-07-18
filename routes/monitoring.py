from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from core.config import (
    MONITOR_DEFAULT_DAYS,
    MONITOR_DRIFT_BASELINE_DAYS,
    MONITOR_DRIFT_RECENT_DAYS,
)
from core.jwt import get_current_staff_user
from db.models import User
from db.session import get_db
from ML import monitoring as mon
from schemas.monitoring import LoanOutcomeCreate, LoanOutcomeResponse

monitoring_route = APIRouter(prefix="/monitoring", tags=["monitoring"])


@monitoring_route.get("/health")
def monitoring_health(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_staff_user),
):
    """Lightweight model health for staff."""
    return mon.get_health(db)


@monitoring_route.get("/summary")
def monitoring_summary(
    days: int = Query(default=MONITOR_DEFAULT_DAYS, ge=1, le=365),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_staff_user),
):
    """Volume, score mix, probability and latency stats."""
    return mon.get_summary(db, days=days)


@monitoring_route.get("/predictions")
def monitoring_predictions(
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_staff_user),
):
    """Recent predictions (paginated)."""
    return {
        "items": mon.get_recent_predictions(db, limit=limit, offset=offset),
        "limit": limit,
        "offset": offset,
    }


@monitoring_route.get("/drift")
def monitoring_drift(
    baseline_days: int = Query(default=MONITOR_DRIFT_BASELINE_DAYS, ge=1, le=365),
    recent_days: int = Query(default=MONITOR_DRIFT_RECENT_DAYS, ge=1, le=90),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_staff_user),
):
    """Simple feature drift: baseline window vs recent window."""
    return mon.get_drift(
        db, baseline_days=baseline_days, recent_days=recent_days
    )


@monitoring_route.get("/performance")
def monitoring_performance(
    days: int | None = Query(
        default=None,
        ge=1,
        le=3650,
        description="Optional lookback on prediction created_at; omit for all labeled loans",
    ),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_staff_user),
):
    """
    Model performance vs ground truth.

    Requires outcomes recorded via POST /monitoring/outcomes.
    Returns ROC-AUC, precision/recall at threshold, confusion matrix, etc.
    """
    return mon.get_performance(db, days=days)


@monitoring_route.post("/outcomes", response_model=LoanOutcomeResponse)
def record_outcome(
    body: LoanOutcomeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_staff_user),
):
    """Record or update whether a loan actually defaulted (for performance metrics)."""
    try:
        outcome = mon.upsert_outcome(
            db,
            loan_id=body.loan_id,
            defaulted=body.defaulted,
            recorded_by_user_id=current_user.id,
            notes=body.notes,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return LoanOutcomeResponse(
        id=outcome.id,
        loan_id=outcome.loan_id,
        defaulted=outcome.defaulted,
        recorded_at=outcome.recorded_at.isoformat() if outcome.recorded_at else "",
        notes=outcome.notes,
    )
