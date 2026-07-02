from db.session import Base, engine
from db.models import User, LoanApplication, LoanPredictionResult

Base.metadata.create_all(bind=engine)
