from pydantic import BaseModel, Field 
from typing import Optional 

class LoanApplication(BaseModel):
    Age: int = Field(..., description="Applicant's age in years")
    Annual_Income: float = Field(..., description="Applicant's annual income")
    Loan_Amount: float = Field(..., description='Requested loan amount')
    Credit_Score: int = Field(..., description='Applicant credit score')
    Months_Employed: int = Field(..., description='How long the applicant has been employed in months')
    Interest_Rate: float = Field(..., description='Agreed interest rate for the loan')
    Loan_Term: int = Field(..., description='Loan duration in months')
    Debt_to_income_ratio: float = Field(..., description='Ratio of debt to income')
    Education_Level: str = Field(..., description='Highest education level attained by the applicant')
    Type_of_Employment: str = Field(..., description='Type of employment (e.g., full-time, part-time, self-employed)')
    Marital_Status: str = Field(..., description='Marital status of the applicant')
    Has_Dependents: bool = Field(..., description='Whether the applicant has dependents')
    Purpose_of_Loan: str = Field(..., description='Purpose for which the loan is requested')
    Has_Guarantor: bool = Field(..., description='Whether the applicant has a guarantor for the loan')
    


class LoanPredictionResponse(BaseModel):
    probability_of_default: float = Field(..., description='Probability that the applicant will default on the loan')
    Risk_level: str = Field(..., description='Risk level of the loan application (e.g., Low, Medium, High)')


    
class config:
    from_attritubes = True



