from sqlalchemy import Column, Integer, String, ForiegnKey, Float, Datetime, Boolean 
from sqlalchemy.orm  import relationship  
from datetime import datetime
from db.session import Base  


class User(Base):
    __tablename__ = 'Users'

    id = Column (Integer, primary_key=True, index=True)
    Username = Column  (String, unique=True, nullable=False, index=True)
    Email_Address = Column (String, unqiue=True, nullable=False, Index=True)
    hashed_password = Column (String, nullable=False)



class LoanRecord(Base):
    __tablename__ = 'LoanRecords'

    Age = Column (Integer, index=True, nullable=False)
    Annual_Income = Column (String, index=True, nullable=False)
    Loan_Amount = Column(Integer, index=True, nullable=False)
    Debt_to_income_ratio = Column (Integer, index=True, nullable=False)
    Education_Level = Column (String, index=True, nullable=False)
    Type_of_Employment = Column (String, index=True, nullable=False)
    Marital_Status = Column (String, Index=True, nullable=False)
    Has_Dependents = Column (Boolean, Index=True, nullable=False)
    Purpose_of_Loan = Column (String, Index=True, nullable=False)
    Has_Guarantor = Column(Boolean, Index=True, nullable=False)











    