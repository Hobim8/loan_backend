from sqlalchemy import Column, Integer, String, ForiegnKey, Float, Datetime
from sqlalchemy.orm  import relationship  
from datetime import datetime
from app.db.session import Base  


class User(Base):
    __tablename__ = 'Users'

    id = Column (Integer, primary_key=True, index=True)
    Username = Column  (String, unique=True, nullable=False, index=True)
    Email_Address = Column (String, unqiue=True, nullable=False, Index=True)
    hashed_password = Column (String, nullable=False)



class LoanRecord(Base):
    __tablename__ = 'LoanRecords'