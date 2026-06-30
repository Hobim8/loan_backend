from ML.engine import predict_default 


result = predict_default({  
    'Age': 30,
    'Annual_Income': 500000,
    'Loan_Amount': 100000,
    'Credit_Score': 650,
    'Months_Employed': 24,
    'Interest_Rate': 5.5,
    'Loan_Term': 12,
    'Debt_to_Income_Ratio': 0.3,
    'Education_Level': "Bachelor's",
    'Type_of_Employment': 'Full-time',
    'Marital_Status': 'Single',
    'Has_Guarantor': 'Yes',
    'Has_Dependents': 'No',
    'Purpose_of_Loan': 'Auto'
})  

print(result)