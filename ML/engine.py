import joblib
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).parent

model = joblib.load(BASE_DIR / "loan_risk_default_model.pkl")
encoder = joblib.load(BASE_DIR / "label_encoders.pkl")

with open(BASE_DIR / "final_threshold.txt", "r") as f:
    THRESHOLD = float(f.read())


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
        "Age": "Age",
        "Annual_Income": "Annual Income (₦)",
        "Loan_Amount": "Loan Amount (₦)",
        "Credit_Score": "Credit Score",
        "Months_Employed": "Months Employed",
        "Interest_Rate": "Interest Rate (%)",
        "Loan_Term": "Loan Term (Months)",
        "Debt_to_Income_Ratio": "Debt-to-Income Ratio",
        "Education_Level": "Education Level",
        "Type_of_Employment": "Type of Employment",
        "Marital_Status": "Marital Status",
        "Has_Guarantor": "Has Guarantor?",
        "Has_Dependents": "Has Dependents?",
        "Purpose_of_Loan": "Purpose of Loan",
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

    return {
        "default_probability": round(float(probability), 4),
        "threshold": THRESHOLD,
        "prediction": "Likely to Default" if risk_flag else "Not Likely to Default",
        "risk_flag": risk_flag,
    }
