import io
import os
from dotenv import load_dotenv
import joblib
import pandas as pd
from supabase import create_client

load_dotenv()

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

supabase = create_client(supabase_url, supabase_key)

model_bytes = supabase.storage.from_("loan risk default model").download("loan_risk_default_model.pkl")
model = joblib.load(io.BytesIO(model_bytes))

encoder_bytes = supabase.storage.from_("loan risk default model").download("label_encoders.pkl")
encoder = joblib.load(io.BytesIO(encoder_bytes))

threshold_bytes = supabase.storage.from_("loan risk default model").download("final_threshold.txt")
THRESHOLD = float(threshold_bytes.decode("utf-8")) 


FEATURE_ORDER = [
    "Age",
    "Annual Income (₦)",
    "Loan Amount (₦)",
    "Credit Score",
    "Months Employed",
    "Interest Rate (%)",
    "Loan Term (Months)",
    "Debt-to-Income Ratio",
    "Education Level",
    "Type of Employment",
    "Marital Status",
    "Has Guarantor?",
    "Has Dependents?",
    "Purpose of Loan",
]


def preprocess(input_data: dict) -> pd.DataFrame:
    df = pd.DataFrame([input_data])

    rename_map = {
        "age": "Age",
        "annual_Income": "Annual Income (₦)",
        "loan_Amount": "Loan Amount (₦)",
        "credit_score": "Credit Score",
        "months_employed": "Months Employed",
        "interest_rate": "Interest Rate (%)",
        "loan_term": "Loan Term (Months)",
        "debt_to_income_ratio": "Debt-to-Income Ratio",
        "education_Level": "Education Level",
        "type_of_Employment": "Type of Employment",
        "marital_Status": "Marital Status",
        "has_Guarantor": "Has Guarantor?",
        "has_Dependents": "Has Dependents?",
        "purpose_of_Loan": "Purpose of Loan",
    }

    df = df.rename(columns=rename_map)

    for col, enc in encoder.items():
        df[col] = enc.transform(df[col])

    df = df[FEATURE_ORDER]

    return df


def predict_default(input_data: dict) -> dict:
    processed_df = preprocess(input_data)

    probability = model.predict_proba(processed_df)[:, 1][0]
    risk_flag = int(probability >= THRESHOLD)

    if probability < 0.4:
        risk_level = "Low"
    elif probability < 0.7:
        risk_level = "Medium"
    else:
        risk_level = "High"
    
    return {
        "default_probability": round(float(probability), 4),
        "threshold": THRESHOLD,
        "prediction": "Likely to Default" if risk_flag else "Not Likely to Default",
        "risk_flag": risk_flag,
        "risk_level": risk_level 
    }


