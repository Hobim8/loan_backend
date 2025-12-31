from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime, Boolean 
from sqlalchemy.orm  import relationship  
from datetime import datetime
from db.session import Base  


class User(Base):
    __tablename__ = 'Users'

    id = Column (Integer, primary_key=True, index=True)
    username = Column  (String, unique=True, nullable=False, index=True)
    email = Column (String, unqiue=True, nullable=False, Index=True)
    hashed_password = Column (String, nullable=False)
    is_active = Column (Boolean, default=False)
    is_staff = Column (Boolean, default=False)

class LoanRecord(Base):
    __tablename__ = 'LoanRecords'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column (Integer, ForeignKey('user.id'), nullable = False, index=True)
    age = Column (Integer, index=True, nullable=False)
    annual_Income = Column (String, index=True, nullable=False)
    loan_Amount = Column(Integer, index=True, nullable=False)
    credit_score = Column(Integer, index=True, nullable=False)
    debt_to_income_ratio = Column (Integer, index=True, nullable=False)
    education_Level = Column (String, index=True, nullable=False)
    type_of_Employment = Column (String, index=True, nullable=False)
    marital_Status = Column (String, Index=True, nullable=False)
    has_Dependents = Column (Boolean, Index=True, nullable=False)
    purpose_of_Loan = Column (String, Index=True, nullable=False)
    has_Guarantor = Column(Boolean, Index=True, nullable=False)

class LoanPredictionResult(Base):
    __table_name___ = 'LoanPredictionResult'

    probability_of_default = Column(Float, Index=True, nullable=False)
    prediction = Column(Boolean, Index=True, nullable=False)
    Risk_level= Column(String, Index=True, nullable=False)









    