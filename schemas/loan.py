from pydantic import BaseModel, Field 
from typing import Optional 

class LoanApplication(BaseModel):
    age: int = Field(..., description="Applicant's age in years")
    annual_Income: float = Field(..., description="Applicant's annual income")
    loan_Amount: float = Field(..., description='Requested loan amount')
    credit_Score: int = Field(..., description='Applicant credit score')
    months_Employed: int = Field(..., description='How long the applicant has been employed in months')
    Interest_Rate: float = Field(..., description='Agreed interest rate for the loan')
    loan_Term: int = Field(..., description='Loan duration in months')
    debt_to_income_ratio: float = Field(..., description='Ratio of debt to income')
    education_Level: str = Field(..., description='Highest education level attained by the applicant')
    type_of_Employment: str = Field(..., description='Type of employment (e.g., full-time, part-time, self-employed)')
    marital_Status: str = Field(..., description='Marital status of the applicant')
    has_Dependents: bool = Field(..., description='Whether the applicant has dependents')
    purpose_of_Loan: str = Field(..., description='Purpose for which the loan is requested')
    has_Guarantor: bool = Field(..., description='Whether the applicant has a guarantor for the loan')
    




class LoanPredictionResponse(BaseModel):
    probability_of_default: float = Field(..., description='Probability that the applicant will default on the loan')
    prediction: bool = Field(..., description='Will default: True or False')
    Risk_level: str = Field(..., description='Risk level of the loan application (e.g., Low, Medium, High)')


    
class config:
    from_attributes = True



