from db.session import Base, engine
from db.models import UserCreate, LoanApplication, LoanPredictionResult


Base.metadata.create_all(bind=engine)

