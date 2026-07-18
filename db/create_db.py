from db.session import Base, engine
from db.models import (
    User,
    LoanApplication,
    LoanPredictionResult,
    LoanOutcome,
    EmailVerification,
)

Base.metadata.create_all(bind=engine)
