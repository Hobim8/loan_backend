
# Loan Default Risk Prediction API
 
A production-grade REST API that predicts the probability of loan default using a trained CatBoost machine learning model. Built with FastAPI, PostgreSQL, and Supabase, with JWT authentication, email verification, and cloud model serving.
 
---
 
## Overview
 
This project demonstrates a complete ML model deployment pipeline — from data ingestion and model training to a secured, cloud-connected API with prediction logging and user management. It is designed to reflect real-world ML engineering practices rather than toy examples.
 
---
 
## Features
 
- **ML Inference Endpoint** — Accepts loan applicant data and returns a default probability score, risk flag, and risk level classification (Low / Medium / High)
- **Cloud Model Serving** — Model artifacts (CatBoost classifier, label encoders, decision threshold) are stored in Supabase Storage and loaded at startup, keeping the codebase lightweight and model versioning decoupled from deployment
- **JWT Authentication** — Secure signup and login with bcrypt password hashing and JSON Web Token issuance
- **Email Verification** — Users must verify their email address via a time-limited OTP before accessing the API
- **Prediction Logging** — Every prediction is persisted to a cloud PostgreSQL database alongside the original loan application data, enabling monitoring and audit trails
- **Input Validation** — Pydantic schemas enforce strict type and enum validation on all incoming requests, preventing invalid data from reaching the model
- **Protected Endpoints** — All prediction routes require a valid JWT token
---
 
## Tech Stack
 
| Layer | Technology |
|---|---|
| API Framework | FastAPI |
| ML Model | CatBoost Classifier |
| Feature Encoding | Scikit-learn Label Encoders |
| Database ORM | SQLAlchemy |
| Database | PostgreSQL (Supabase) |
| Model Storage | Supabase Storage |
| Authentication | JWT (python-jose) |
| Password Hashing | Passlib + bcrypt |
| Email Service | Resend |
| Data Validation | Pydantic v2 |
| Package Manager | uv |
 
---
 
## Project Structure
 
```
loan_backend/
├── app/
│   └── main.py               # FastAPI app entry point, router registration
├── core/
│   ├── auth.py               # Signup, Login, Email Verification endpoints
│   ├── config.py             # Environment variable loading
│   ├── email.py              # Verification code generation and email sending
│   ├── jwt.py                # Token creation and current user dependency
│   └── security.py           # Password hashing and verification
├── db/
│   ├── create_db.py          # Table creation script
│   ├── models.py             # SQLAlchemy ORM models
│   └── session.py            # Database engine and session factory
├── ML/
│   └── engine.py             # Model loading from Supabase, preprocessing, prediction
├── routes/
│   └── loan.py               # Loan prediction endpoint
├── schemas/
│   ├── loan.py               # Loan application and prediction response schemas
│   └── user.py               # User registration, login, and email verification schemas
├── .env                      # Environment variables (not committed)
├── requirements.txt          # Project dependencies
└── Dockerfile                # Container configuration
```
 
---
 
## API Endpoints
 
### Authentication
 
| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/Signup` | Register a new user |
| POST | `/auth/Login` | Login and receive JWT token |
| POST | `/auth/verify-email` | Verify email with OTP code |
 
### Prediction
 
| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| POST | `/loan/predict` | Submit loan application and get default prediction | Yes |
 
---
 
## Prediction Input
 
```json
{
  "age": 35,
  "annual_Income": 1200000,
  "loan_Amount": 500000,
  "credit_score": 620,
  "months_employed": 48,
  "interest_rate": 12.5,
  "loan_term": 24,
  "debt_to_income_ratio": 0.45,
  "education_Level": "Bachelor's",
  "type_of_Employment": "Full-time",
  "marital_Status": "Married",
  "has_Guarantor": "No",
  "has_Dependents": "Yes",
  "purpose_of_Loan": "Business"
}
```
 
### Prediction Response
 
```json
{
  "default_probability": 0.6814,
  "threshold": 0.25,
  "prediction": "Likely to Default",
  "risk_flag": 1,
  "risk_level": "Medium"
}
```
 
---
 
## ML Model Details
 
- **Algorithm**: CatBoost Classifier
- **Training Data**: Loan applicant dataset with 14 features
- **Custom Decision Threshold**: 0.25 (tuned for higher sensitivity to default risk)
- **Feature Engineering**: Label encoding for categorical variables via Scikit-learn
- **Model Artifacts**: Stored in Supabase Storage, loaded at application startup
The custom threshold of 0.25 means the model flags applicants as high-risk at a lower probability than the default 0.50, prioritising recall of actual defaults over precision. This reflects a real lending institution's preference to minimise bad loans even at the cost of some false positives.
 
---
 
## Setup and Installation
 
### Prerequisites
 
- Python 3.11+
- uv package manager
- Supabase account (PostgreSQL database + Storage)
- Resend account (email delivery)
### Environment Variables
 
Create a `.env` file in the project root:
 
```env
DATABASE_URL=postgresql+psycopg2://user:password@host:port/dbname?sslmode=require
SECRET_KEY=your_jwt_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_service_role_key
RESEND_API_KEY=re_your_resend_api_key
```
 
### Installation
 
```bash
git clone https://github.com/Hobim8/loan_backend.git
cd loan_backend
uv venv
uv pip install -r requirements.txt
```
 
### Database Setup
 
```bash
python -m db.create_db
```
 
### Run the API
 
```bash
uvicorn app.main:app --reload
```
 
Visit `http://127.0.0.1:8000/docs` to explore the API via Swagger UI.
 
---
 
## Key Engineering Decisions
 
**Why CatBoost?** CatBoost handles categorical features natively and is highly performant on tabular data with minimal hyperparameter tuning, making it well suited for loan risk datasets with mixed feature types.
 
**Why a custom threshold?** The default 0.50 threshold optimises for accuracy. Lowering it to 0.25 increases sensitivity to default risk, which is the correct objective for a lending institution where the cost of a missed default is higher than the cost of a rejected good applicant.
 
**Why Supabase Storage for models?** Storing model artifacts in the repository bloats git history, ties model versions to code deployments, and creates version drift issues across environments. Cloud storage decouples model versioning from application deployment.
 
**Why email verification?** Unverified accounts are a common attack vector for abuse and spam. Requiring email verification before API access ensures users control the email they registered with and reduces fraudulent account creation.
 
---
 
## Author
 
Victor — Backend and AI/ML Engineer  
GitHub: [Hobim8](https://github.com/Hobim8)
