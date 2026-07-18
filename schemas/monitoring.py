from typing import Any, Optional

from pydantic import BaseModel, Field


class LoanOutcomeCreate(BaseModel):
    loan_id: int = Field(..., description="LoanRecords.id to attach the outcome to")
    defaulted: bool = Field(..., description="True if the borrower defaulted")
    notes: Optional[str] = Field(None, description="Optional free-text notes")


class LoanOutcomeResponse(BaseModel):
    id: int
    loan_id: int
    defaulted: bool
    recorded_at: str
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class MonitoringSummary(BaseModel):
    window_days: int
    model_version_config: str
    total_predictions: int
    success_count: int
    error_count: int
    error_rate: float
    positive_rate: Optional[float] = None
    risk_level_mix: dict[str, int]
    probability: dict[str, Any]
    latency_ms: dict[str, Any]


class MonitoringHealth(BaseModel):
    model_version: str
    total_predictions: int
    predictions_last_24h: int
    errors_last_24h: int
    error_rate_last_24h: float
    last_prediction_at: Optional[str] = None
    last_prediction_status: Optional[str] = None
    outcomes_recorded: int
    predictions_with_outcomes: int
    status: str


class PredictionListItem(BaseModel):
    id: int
    loan_id: int
    created_at: Optional[str] = None
    probability_of_default: float
    prediction: str
    risk_level: str
    risk_flag: int
    latency_ms: Optional[float] = None
    model_version: Optional[str] = None
    threshold_used: Optional[float] = None
    status: Optional[str] = None
