"""Prometheus metrics for loan model inference."""

from prometheus_client import Counter, Histogram

PREDICTIONS_TOTAL = Counter(
    "loan_model_predictions_total",
    "Total loan default predictions",
    ["status", "risk_level", "model_version"],
)

PREDICTION_ERRORS_TOTAL = Counter(
    "loan_model_prediction_errors_total",
    "Total failed loan default predictions",
    ["model_version"],
)

PREDICTION_LATENCY = Histogram(
    "loan_model_prediction_latency_seconds",
    "Loan model inference latency in seconds",
    ["model_version"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
)

PREDICTION_PROBABILITY = Histogram(
    "loan_model_default_probability",
    "Predicted probability of default",
    ["model_version"],
    buckets=(0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 1.0),
)

DEFAULT_FLAG_TOTAL = Counter(
    "loan_model_default_flag_total",
    "Predictions flagged as likely to default (risk_flag=1)",
    ["model_version"],
)


def record_prediction_success(
    *,
    model_version: str,
    risk_level: str,
    probability: float,
    risk_flag: int,
    latency_seconds: float,
) -> None:
    PREDICTIONS_TOTAL.labels(
        status="success",
        risk_level=risk_level,
        model_version=model_version,
    ).inc()
    PREDICTION_LATENCY.labels(model_version=model_version).observe(latency_seconds)
    PREDICTION_PROBABILITY.labels(model_version=model_version).observe(probability)
    if risk_flag:
        DEFAULT_FLAG_TOTAL.labels(model_version=model_version).inc()


def record_prediction_error(*, model_version: str, latency_seconds: float) -> None:
    PREDICTIONS_TOTAL.labels(
        status="error",
        risk_level="unknown",
        model_version=model_version,
    ).inc()
    PREDICTION_ERRORS_TOTAL.labels(model_version=model_version).inc()
    PREDICTION_LATENCY.labels(model_version=model_version).observe(latency_seconds)
