from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime, Boolean 
from sqlalchemy.orm  import relationship  
from datetime import datetime
from db.session import Base  
from sqlalchemy import Enum as SAEnum
from enum import Enum

class EducationLevel(Enum):
    HIGH_SCHOOL = "High School"
    BACHELORS = "Bachelors"
    MASTERS = "Masters"
    PHD = "PhD"

class type_of_Employment(Enum):
    FULL_TIME = "Full-time"
    PART_TIME = "Part-time"
    SELF_EMPLOYED ="Self-employed"
    UNEMPLOYED = "unemployed"

class marital_Status(Enum):
    MARRIED = "Married"
    DIVORCED ="Divorced"
    SINGLE ="Single"


class purpose_of_Loan(Enum):
    AUTO ="Auto"
    BUSINESS ="Business"
    HOME ="Home"
    OTHER = "Other"


class UserCreate(Base):
    __tablename__ = 'Users'

    id = Column (Integer, primary_key=True, index=True)
    username = Column  (String, unique=True, nullable=False, index=True)
    email = Column (String, unique=True, nullable=False, index=True)
    hashed_password = Column (String, nullable=False)
    is_active = Column (Boolean, default=False)
    is_staff = Column (Boolean, default=False)
    loans = relationship('LoanApplication',back_populates='UserCreate')

class LoanApplication(Base):
    __tablename__ = 'LoanRecords'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column (Integer, ForeignKey('Users.id'), nullable = False, index=True)
    age = Column (Integer, index=True, nullable=False)
    annual_Income = Column (String, index=True, nullable=False)
    loan_Amount = Column(Integer, index=True, nullable=False)
    credit_score = Column(Integer, index=True, nullable=False)
    debt_to_income_ratio = Column (Integer, index=True, nullable=False)
    education_Level = Column (SAEnum(EducationLevel), nullable=False, index=True)
    type_of_Employment = Column (SAEnum(type_of_Employment), nullable=False, index=True)
    marital_Status = Column (SAEnum(marital_Status), nullable=False, index=True)
    has_Dependents = Column (Boolean, index=True, nullable=False)
    purpose_of_Loan = Column (SAEnum(purpose_of_Loan), nullable=False, index=True)
    has_Guarantor = Column(Boolean, index=True, nullable=False)
    users = relationship('UserCreate',back_populates='LoanApplication')

class LoanPredictionResult(Base):
    __tablename__ = 'LoanPredictionResult'
    id = Column(Integer, primary_key=True, nullable=False, index=True)
    Loan_id = Column(Integer, ForeignKey('LoanRecords.id'), index=True, nullable=False)
    probability_of_default = Column(Float, index=True, nullable=False)
    prediction = Column(Boolean, index=True, nullable=False)
    Risk_level= Column(String, index=True, nullable=False)









    