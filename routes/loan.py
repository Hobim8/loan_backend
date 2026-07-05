from schemas.loan import LoanApplication, LoanPredictionResult
from db.session import get_db
from db.models import LoanApplication as LoanApplicationModel
from db.models import LoanPredictionResult as LoanPredictionResultModel
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from ML.engine import predict_default
