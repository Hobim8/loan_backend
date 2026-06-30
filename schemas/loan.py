from pydantic import BaseModel, Field 
from typing import Optional 
from enum import Enum 


class EducationLevel(str, Enum):
    BACHELORS = "Bachelor's"
    HIGH_SCHOOL = "High School"
    MASTERS = "Master's"
    PHD ="PhD"


class TypeofEmployment(str, Enum):
    FULL_TIME = 'Full-time'
    PART_TIME = 'Part-time'
    SELF_EMPLOYED = 'Self-employed'
    UNEMPLOYED = 'Unemployed'



class MaritalStatus(str, Enum):
    DIVORCED = 'Divorced'
    MARRIED = 'Married'
    SINGLE = 'Single'
    
class PurposeofLoan(str, Enum):
    AUTO = 'Auto'
    BUSINESS = 'Business'
    EDUCATION = 'Education'
    HOME = 'Home'
    OTHER = 'Other'

class HasGuarantor(str, Enum):
    NO = 'No'
    YES = 'Yes'

class HasDependents(str, Enum):
    NO = 'No'
    YES = 'Yes'

class LoanApplication(BaseModel):
    Age: int = Field(..., description="Applicant's age in years")
    Annual_Income: float = Field(..., description="Applicant's annual income")
    Loan_Amount: float = Field(..., description='Requested loan amount')
    Credit_Score: int = Field(..., description='Applicant credit score')
    Months_Employed: int = Field(..., description='How long the applicant has been employed in months')
    Interest_Rate: float = Field(..., description='Agreed interest rate for the loan')
    Loan_Term: int = Field(..., description='Loan duration in months')
    Debt_to_Income_Ratio: float = Field(..., description='Ratio of debt to income')
    Education_Level: EducationLevel = Field(..., description='Highest education level attained by the applicant')
    Type_of_Employment: TypeofEmployment = Field(..., description='Type of employment (e.g., full time, part time, self employed)')
    Marital_Status: MaritalStatus = Field(..., description='Marital status of the applicant')
    Has_Guarantor: HasGuarantor = Field(..., description='Whether the applicant has a guarantor for the loan')
    Has_Dependents: HasDependents = Field(..., description='Whether the applicant has dependents')
    Purpose_of_Loan: PurposeofLoan = Field(..., description='Purpose for which the loan is requested')

class LoanPredictionResult(BaseModel):
    probability_of_default: float = Field(..., description='Probability that the applicant will default on the loan')
    prediction: bool = Field(..., description='Will default: True or False')
    Risk_level: str = Field(..., description='Risk level of the loan application (e.g., Low, Medium, High)')


    
class config:
    from_attributes = True



