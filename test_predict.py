from ML.engine import predict_default 


result = predict_default({
    'age': 30,
    'annual_Income': 500000,
    'loan_Amount': 100000,
    'credit_score': 650,
    'months_employed': 24,
    'interest_rate': 5.5,
    'loan_term': 12,
    'debt_to_income_ratio': 0.3,
    'education_Level': "Bachelor's",
    'type_of_Employment': 'Full-time',
    'marital_Status': 'Single',
    'has_Guarantor': 'Yes',
    'has_Dependents': 'No',
    'purpose_of_Loan': 'Auto'
}) 

print(result)