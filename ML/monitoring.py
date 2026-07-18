"""Aggregation helpers for staff model-monitoring APIs."""

from __future__ import annotations

from datetime import datetime, timedelta
from statistics import mean
from typing import Any, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from core.config import MODEL_VERSION
from db.models import LoanApplication, LoanOutcome, LoanPredictionResult

NUMERIC_FEATURES = [
    "age",
    "annual_Income",
    "loan_Amount",
    "credit_score",
    "months_employed",
    "interest_rate",
    "loan_term",
    "debt_to_income_ratio",
]

CATEGORICAL_FEATURES = [
    "education_Level",
    "type_of_Employment",
    "marital_Status",
    "has_Dependents",
    "purpose_of_Loan",
    "has_Guarantor",
]


def _window_start(days: int) -> datetime:
    return datetime.utcnow() - timedelta(days=days)


def _percentile(sorted_vals: list[float], p: float) -> Optional[float]:
    if not sorted_vals:
        return None
    if len(sorted_vals) == 1:
        return float(sorted_vals[0])
    k = (len(sorted_vals) - 1) * p
    f = int(k)
    c = min(f + 1, len(sorted_vals) - 1)
    if f == c:
        return float(sorted_vals[f])
    return float(sorted_vals[f] + (sorted_vals[c] - sorted_vals[f]) * (k - f))


def get_summary(db: Session, days: int) -> dict[str, Any]:
    since = _window_start(days)
    rows = (
        db.query(LoanPredictionResult)
        .filter(LoanPredictionResult.created_at >= since)
        .all()
    )

    total = len(rows)
    success = [r for r in rows if (r.status or "success") == "success"]
    errors = total - len(success)

    probs = [r.probability_of_default for r in success if r.probability_of_default is not None]
    latencies = [r.latency_ms for r in success if r.latency_ms is not None]
    flags = [r.Risk_flag for r in success if r.Risk_flag is not None]

    risk_mix: dict[str, int] = {}
    for r in success:
        level = r.Risk_level or "unknown"
        risk_mix[level] = risk_mix.get(level, 0) + 1

    probs_sorted = sorted(probs)
    lat_sorted = sorted(latencies)

    positive_rate = (sum(1 for f in flags if f == 1) / len(flags)) if flags else None

    return {
        "window_days": days,
        "model_version_config": MODEL_VERSION,
        "total_predictions": total,
        "success_count": len(success),
        "error_count": errors,
        "error_rate": (errors / total) if total else 0.0,
        "positive_rate": round(positive_rate, 4) if positive_rate is not None else None,
        "risk_level_mix": risk_mix,
        "probability": {
            "count": len(probs),
            "mean": round(mean(probs), 4) if probs else None,
            "min": round(min(probs), 4) if probs else None,
            "max": round(max(probs), 4) if probs else None,
            "p50": round(_percentile(probs_sorted, 0.5), 4) if probs_sorted else None,
            "p95": round(_percentile(probs_sorted, 0.95), 4) if probs_sorted else None,
        },
        "latency_ms": {
            "count": len(latencies),
            "mean": round(mean(latencies), 2) if latencies else None,
            "max": round(max(latencies), 2) if latencies else None,
            "p50": round(_percentile(lat_sorted, 0.5), 2) if lat_sorted else None,
            "p95": round(_percentile(lat_sorted, 0.95), 2) if lat_sorted else None,
        },
    }


def get_health(db: Session) -> dict[str, Any]:
    total = db.query(func.count(LoanPredictionResult.id)).scalar() or 0
    last = (
        db.query(LoanPredictionResult)
        .order_by(LoanPredictionResult.created_at.desc())
        .first()
    )
    since_24h = _window_start(1)
    recent = (
        db.query(LoanPredictionResult)
        .filter(LoanPredictionResult.created_at >= since_24h)
        .all()
    )
    recent_total = len(recent)
    recent_errors = sum(1 for r in recent if (r.status or "success") != "success")

    outcomes_total = db.query(func.count(LoanOutcome.id)).scalar() or 0
    labeled = (
        db.query(func.count(LoanPredictionResult.id))
        .join(LoanOutcome, LoanOutcome.loan_id == LoanPredictionResult.Loan_id)
        .scalar()
        or 0
    )

    return {
        "model_version": MODEL_VERSION,
        "total_predictions": total,
        "predictions_last_24h": recent_total,
        "errors_last_24h": recent_errors,
        "error_rate_last_24h": (recent_errors / recent_total) if recent_total else 0.0,
        "last_prediction_at": last.created_at.isoformat() if last and last.created_at else None,
        "last_prediction_status": last.status if last else None,
        "outcomes_recorded": outcomes_total,
        "predictions_with_outcomes": labeled,
        "status": "ok" if recent_errors == 0 else "degraded",
    }


def get_recent_predictions(
    db: Session, *, limit: int = 50, offset: int = 0
) -> list[dict[str, Any]]:
    rows = (
        db.query(LoanPredictionResult)
        .order_by(LoanPredictionResult.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return [
        {
            "id": r.id,
            "loan_id": r.Loan_id,
            "created_at": r.created_at.isoformat() if r.created_at else None,
            "probability_of_default": r.probability_of_default,
            "prediction": r.prediction,
            "risk_level": r.Risk_level,
            "risk_flag": r.Risk_flag,
            "latency_ms": r.latency_ms,
            "model_version": r.model_version,
            "threshold_used": r.threshold_used,
            "status": r.status,
        }
        for r in rows
    ]


def _feature_stats(values: list[float]) -> dict[str, Optional[float]]:
    if not values:
        return {"count": 0, "mean": None, "std": None}
    m = mean(values)
    if len(values) < 2:
        std = 0.0
    else:
        std = (sum((v - m) ** 2 for v in values) / (len(values) - 1)) ** 0.5
    return {
        "count": len(values),
        "mean": round(m, 4),
        "std": round(std, 4),
    }


def get_drift(
    db: Session, *, baseline_days: int, recent_days: int
) -> dict[str, Any]:
    now = datetime.utcnow()
    recent_start = now - timedelta(days=recent_days)
    baseline_end = recent_start
    baseline_start = now - timedelta(days=baseline_days + recent_days)

    baseline_rows = (
        db.query(LoanApplication)
        .filter(
            LoanApplication.created_at >= baseline_start,
            LoanApplication.created_at < baseline_end,
        )
        .all()
    )
    recent_rows = (
        db.query(LoanApplication)
        .filter(LoanApplication.created_at >= recent_start)
        .all()
    )

    numeric_report = []
    for col in NUMERIC_FEATURES:
        b_vals = [float(getattr(r, col)) for r in baseline_rows if getattr(r, col) is not None]
        r_vals = [float(getattr(r, col)) for r in recent_rows if getattr(r, col) is not None]
        b_stats = _feature_stats(b_vals)
        r_stats = _feature_stats(r_vals)

        shift_flag = False
        mean_delta = None
        if b_stats["mean"] is not None and r_stats["mean"] is not None:
            mean_delta = round(r_stats["mean"] - b_stats["mean"], 4)
            b_std = b_stats["std"] or 0.0
            # Flag if recent mean moves > 1 baseline std (simple heuristic)
            if b_std > 0 and abs(mean_delta) > b_std:
                shift_flag = True
            elif b_std == 0 and mean_delta != 0:
                shift_flag = True

        numeric_report.append(
            {
                "feature": col,
                "baseline": b_stats,
                "recent": r_stats,
                "mean_delta": mean_delta,
                "possible_drift": shift_flag,
            }
        )

    categorical_report = []
    for col in CATEGORICAL_FEATURES:
        def shares(rows: list) -> dict[str, float]:
            if not rows:
                return {}
            counts: dict[str, int] = {}
            for r in rows:
                v = str(getattr(r, col))
                counts[v] = counts.get(v, 0) + 1
            n = len(rows)
            return {k: round(v / n, 4) for k, v in counts.items()}

        b_share = shares(baseline_rows)
        r_share = shares(recent_rows)
        keys = set(b_share) | set(r_share)
        max_shift = 0.0
        for k in keys:
            max_shift = max(max_shift, abs(r_share.get(k, 0.0) - b_share.get(k, 0.0)))
        categorical_report.append(
            {
                "feature": col,
                "baseline_share": b_share,
                "recent_share": r_share,
                "max_share_shift": round(max_shift, 4),
                "possible_drift": max_shift >= 0.15,
            }
        )

    return {
        "baseline_window_days": baseline_days,
        "recent_window_days": recent_days,
        "baseline_count": len(baseline_rows),
        "recent_count": len(recent_rows),
        "insufficient_data": len(baseline_rows) < 5 or len(recent_rows) < 5,
        "numeric_features": numeric_report,
        "categorical_features": categorical_report,
    }


def get_performance(db: Session, days: Optional[int] = None) -> dict[str, Any]:
    """
    Model performance vs ground-truth outcomes.

    Joins the latest successful prediction per loan with LoanOutcome.defaulted.
    """
    q = (
        db.query(LoanPredictionResult, LoanOutcome)
        .join(LoanOutcome, LoanOutcome.loan_id == LoanPredictionResult.Loan_id)
        .filter((LoanPredictionResult.status == "success") | (LoanPredictionResult.status.is_(None)))
    )
    if days is not None:
        q = q.filter(LoanPredictionResult.created_at >= _window_start(days))

    pairs = q.all()

    # Keep latest prediction per loan
    by_loan: dict[int, tuple[LoanPredictionResult, LoanOutcome]] = {}
    for pred, outcome in pairs:
        existing = by_loan.get(pred.Loan_id)
        if existing is None:
            by_loan[pred.Loan_id] = (pred, outcome)
        else:
            prev, _ = existing
            if (pred.created_at or datetime.min) >= (prev.created_at or datetime.min):
                by_loan[pred.Loan_id] = (pred, outcome)

    if not by_loan:
        return {
            "labeled_count": 0,
            "message": "No predictions with recorded outcomes yet. "
            "Record outcomes via POST /monitoring/outcomes.",
            "metrics": None,
        }

    y_true: list[int] = []
    y_score: list[float] = []
    y_pred_flag: list[int] = []

    for pred, outcome in by_loan.values():
        y_true.append(1 if outcome.defaulted else 0)
        y_score.append(float(pred.probability_of_default))
        y_pred_flag.append(int(pred.Risk_flag))

    n = len(y_true)
    n_pos = sum(y_true)
    n_neg = n - n_pos

    tp = sum(1 for t, p in zip(y_true, y_pred_flag) if t == 1 and p == 1)
    tn = sum(1 for t, p in zip(y_true, y_pred_flag) if t == 0 and p == 0)
    fp = sum(1 for t, p in zip(y_true, y_pred_flag) if t == 0 and p == 1)
    fn = sum(1 for t, p in zip(y_true, y_pred_flag) if t == 1 and p == 0)

    precision = tp / (tp + fp) if (tp + fp) else None
    recall = tp / (tp + fn) if (tp + fn) else None
    accuracy = (tp + tn) / n if n else None
    f1 = (
        (2 * precision * recall / (precision + recall))
        if precision is not None and recall is not None and (precision + recall) > 0
        else None
    )

    roc_auc = None
    average_precision = None
    brier = None
    try:
        from sklearn.metrics import (
            average_precision_score,
            brier_score_loss,
            roc_auc_score,
        )

        # AUC needs both classes present
        if n_pos > 0 and n_neg > 0:
            roc_auc = float(roc_auc_score(y_true, y_score))
            average_precision = float(average_precision_score(y_true, y_score))
        brier = float(brier_score_loss(y_true, y_score))
    except Exception:
        pass

    return {
        "window_days": days,
        "labeled_count": n,
        "actual_default_rate": round(n_pos / n, 4) if n else None,
        "metrics": {
            "roc_auc": round(roc_auc, 4) if roc_auc is not None else None,
            "average_precision": round(average_precision, 4)
            if average_precision is not None
            else None,
            "brier_score": round(brier, 4) if brier is not None else None,
            "accuracy": round(accuracy, 4) if accuracy is not None else None,
            "precision_at_threshold": round(precision, 4) if precision is not None else None,
            "recall_at_threshold": round(recall, 4) if recall is not None else None,
            "f1_at_threshold": round(f1, 4) if f1 is not None else None,
            "confusion_matrix": {
                "true_positives": tp,
                "true_negatives": tn,
                "false_positives": fp,
                "false_negatives": fn,
            },
            "note": "Threshold metrics use stored Risk_flag from prediction time. "
            "roc_auc requires at least one default and one non-default outcome.",
        },
    }


def upsert_outcome(
    db: Session,
    *,
    loan_id: int,
    defaulted: bool,
    recorded_by_user_id: Optional[int] = None,
    notes: Optional[str] = None,
) -> LoanOutcome:
    loan = db.query(LoanApplication).filter(LoanApplication.id == loan_id).first()
    if not loan:
        raise ValueError("Loan not found")

    existing = db.query(LoanOutcome).filter(LoanOutcome.loan_id == loan_id).first()
    if existing:
        existing.defaulted = defaulted
        existing.recorded_at = datetime.utcnow()
        existing.recorded_by_user_id = recorded_by_user_id
        existing.notes = notes
        db.commit()
        db.refresh(existing)
        return existing

    outcome = LoanOutcome(
        loan_id=loan_id,
        defaulted=defaulted,
        recorded_by_user_id=recorded_by_user_id,
        notes=notes,
    )
    db.add(outcome)
    db.commit()
    db.refresh(outcome)
    return outcome
