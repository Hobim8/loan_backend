import time

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.config import MODEL_VERSION
from core.jwt import get_current_user
from db.models import LoanApplication as LoanApplicationModel
from db.models import LoanPredictionResult as LoanPredictionResultModel
from db.models import User
from db.session import get_db
from ML.engine import THRESHOLD, predict_default
from ML.prometheus_metrics import record_prediction_error, record_prediction_success
from schemas.loan import LoanApplication

loan_route = APIRouter(prefix="/loan", tags=["loan"])


@loan_route.post("/predict")
def predict(
    loan: LoanApplication,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    loan_info = loan.model_dump()

    loan_record = LoanApplicationModel(user_id=current_user.id, **loan_info)
    db.add(loan_record)
    db.commit()
    db.refresh(loan_record)

    t0 = time.perf_counter()
    try:
        predicted = predict_default(loan_info)
        latency_ms = (time.perf_counter() - t0) * 1000.0

        prediction_record = LoanPredictionResultModel(
            Loan_id=loan_record.id,
            probability_of_default=predicted["default_probability"],
            prediction=predicted["prediction"],
            Risk_level=predicted["risk_level"],
            Risk_flag=predicted["risk_flag"],
            latency_ms=round(latency_ms, 2),
            model_version=MODEL_VERSION,
            threshold_used=float(predicted.get("threshold", THRESHOLD)),
            status="success",
        )
        db.add(prediction_record)
        db.commit()
        db.refresh(prediction_record)

        record_prediction_success(
            model_version=MODEL_VERSION,
            risk_level=predicted["risk_level"],
            probability=float(predicted["default_probability"]),
            risk_flag=int(predicted["risk_flag"]),
            latency_seconds=latency_ms / 1000.0,
        )

        return predicted

    except Exception as exc:
        latency_ms = (time.perf_counter() - t0) * 1000.0
        record_prediction_error(
            model_version=MODEL_VERSION,
            latency_seconds=latency_ms / 1000.0,
        )
        try:
            error_record = LoanPredictionResultModel(
                Loan_id=loan_record.id,
                probability_of_default=0.0,
                prediction="error",
                Risk_level="unknown",
                Risk_flag=0,
                latency_ms=round(latency_ms, 2),
                model_version=MODEL_VERSION,
                threshold_used=float(THRESHOLD),
                status="error",
                error_message=str(exc)[:500],
            )
            db.add(error_record)
            db.commit()
        except Exception:
            db.rollback()

        raise HTTPException(status_code=500, detail="Prediction failed") from exc
