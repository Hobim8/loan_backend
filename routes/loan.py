from schemas.loan import LoanApplication, LoanPredictionResult
from db.session import get_db
from db.models import LoanApplication as LoanApplicationModel
from db.models import LoanPredictionResult as LoanPredictionResultModel
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from ML.engine import predict_default
from core.jwt import get_current_user
from db.models import User

loan_route = APIRouter(prefix="/loan", tags=["loan"])


@loan_route.post("/predict")
def predict(
    loan: LoanApplication,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    LoanInfo = loan.model_dump()

    loan_record = LoanApplicationModel(user_id=current_user.id, **LoanInfo)
    db.add(loan_record)
    db.commit()
    db.refresh(loan_record)

    predicted = predict_default(LoanInfo)

    predictionRecord = LoanPredictionResultModel(
        loan_id=loan_record.id,
        default_probability=predicted["default_probability"],
        prediction=predicted["prediction"],
        risk_level=predicted["risk_level"],
        risk_flag=predicted["risk_flag"],
    )
    db.add(predictionRecord)
    db.commit()
    db.refresh(predictionRecord)

    return predicted
