# Loan Default Risk Prediction API

A production-style REST API that predicts loan default probability with a trained CatBoost model. Built with FastAPI, PostgreSQL (Supabase), JWT auth, email verification, password reset, prediction logging, staff model monitoring, Prometheus metrics, a lightweight web UI, and Docker packaging.

---

## Overview

This project demonstrates an end-to-end ML deployment pipeline: secured API access, cloud model serving, inference with audit logging, and post-deployment model monitoring (health, drift, and performance vs ground truth). It is meant to reflect real ML engineering practices rather than a demo-only notebook API.

---

## Features

### Core ML API
- **ML inference** — Accepts loan applicant features and returns default probability, risk flag, risk level (Low / Medium / High), and the decision threshold used
- **Cloud model serving** — CatBoost model, label encoders, and threshold load from Supabase Storage at startup so model versioning stays decoupled from code deploys
- **Input validation** — Pydantic schemas enforce types and enums before data reaches the model
- **Prediction logging** — Each request stores the application, prediction, latency, model version, and threshold for audit and monitoring

### Auth & users
- **JWT authentication** — Signup / login with bcrypt password hashing and bearer tokens
- **Email verification (OTP)** — Accounts must verify email before login
- **Password reset** — Forgot-password flow with time-limited token, email link, HTML form page, and JSON API reset
- **Staff role** — `is_staff` users can access monitoring APIs

### Monitoring & ops
- **Staff monitoring APIs** — Health, volume/summary stats, recent predictions, simple feature drift, and performance (ROC-AUC, precision/recall, confusion matrix) once outcomes are labeled
- **Loan outcomes** — Staff can record whether a loan actually defaulted for offline performance tracking
- **Prometheus metrics** — `/metrics` scrape endpoint for inference counters, latency, and error signals
- **Health check** — `GET /health` for load balancers and Docker

### Product & packaging
- **Web UI** — “Apex Underwriting” desk served at `/` (static frontend under `frontend/`)
- **Docker** — Single-image `Dockerfile` (Python 3.13 slim + uv); no Compose required (DB and storage stay on Supabase)
- **Email backends** — `console` (print codes/links to logs for local/dev) or `resend` (real delivery)

---

## Tech Stack

| Layer | Technology |
|---|---|
| API framework | FastAPI |
| ML model | CatBoost Classifier |
| Feature encoding | Scikit-learn LabelEncoder |
| ORM | SQLAlchemy |
| Database | PostgreSQL (Supabase) |
| Model storage | Supabase Storage |
| Auth | JWT (`python-jose`) + Passlib/bcrypt |
| Email | Resend or console backend |
| Metrics | Prometheus client |
| Validation | Pydantic v2 |
| Package manager | uv |
| Container | Docker (single service) |

---

## Project Structure

```
loan_backend/
├── app/
│   └── main.py                 # FastAPI app, CORS, routers, /health, /metrics, UI
├── core/
│   ├── auth.py                 # Signup, login, verify-email, password reset
│   ├── config.py               # Env config (auth, monitoring windows, email)
│   ├── email.py                # OTP / reset token generation and sending
│   ├── jwt.py                  # Access tokens; current user & staff deps
│   └── security.py             # Password hash / verify
├── db/
│   ├── create_db.py            # Create tables
│   ├── models.py               # Users, loans, predictions, outcomes, tokens
│   └── session.py              # Engine, SessionLocal, get_db
├── ML/
│   ├── engine.py               # Load model from Supabase, preprocess, predict
│   ├── monitoring.py           # Staff analytics aggregations
│   └── prometheus_metrics.py   # Prediction success/error metrics
├── routes/
│   ├── loan.py                 # POST /loan/predict
│   └── monitoring.py           # Staff monitoring + outcomes
├── schemas/
│   ├── loan.py
│   ├── monitoring.py
│   ├── token.py
│   └── user.py
├── frontend/                   # Apex Underwriting UI (served at /)
│   ├── index.html
│   └── assets/
├── scripts/
│   └── migrate_monitoring.sql  # Optional SQL for monitoring-related schema
├── Dockerfile
├── .dockerignore
├── pyproject.toml
├── uv.lock
├── requirement.txt             # Pinned deps (legacy/alternate install)
└── .env                        # Secrets (not committed)
```

---

## API Endpoints

### System

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| GET | `/` | Apex Underwriting web UI | No |
| GET | `/health` | Liveness probe | No |
| GET | `/metrics` | Prometheus scrape (restrict in production) | No |
| GET | `/docs` | Swagger UI | No |

### Authentication (`/auth`)

| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/Signup` | Register; sends email verification OTP |
| POST | `/auth/Login` | Login with username **or** email; returns JWT |
| POST | `/auth/verify-email` | Verify OTP and activate account |
| POST | `/auth/forgot-password` | Request password-reset email |
| POST | `/auth/reset-password` | Reset password via JSON (Swagger/API) |
| GET | `/auth/reset-password-form` | HTML form opened from email link |
| POST | `/auth/reset-password-form` | HTML form submit |

### Prediction (`/loan`)

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| POST | `/loan/predict` | Score a loan application | JWT (verified user) |

### Monitoring (`/monitoring`) — **staff only**

| Method | Endpoint | Description |
|---|---|---|
| GET | `/monitoring/health` | Lightweight model / pipeline health |
| GET | `/monitoring/summary` | Volume, score mix, probability & latency stats |
| GET | `/monitoring/predictions` | Recent predictions (paginated) |
| GET | `/monitoring/drift` | Feature stats: baseline window vs recent window |
| GET | `/monitoring/performance` | Metrics vs labeled outcomes (AUC, P/R, confusion matrix) |
| POST | `/monitoring/outcomes` | Record or update whether a loan defaulted |

---

## Prediction I/O

### Request (`POST /loan/predict`)

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

### Response

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

- **Algorithm:** CatBoost Classifier  
- **Features:** 14 applicant fields (numeric + categorical)  
- **Encoding:** Scikit-learn label encoders for categoricals  
- **Decision threshold:** 0.25 (higher sensitivity to default risk than 0.50)  
- **Artifacts:** Stored in Supabase Storage; loaded at application startup  
- **Logged metadata:** Probability, risk level/flag, latency, model version, threshold, status  

A threshold of **0.25** flags more applicants as high-risk than a 0.50 cutoff. That trade-off prioritises catching defaults (recall) over minimising false positives—typical when the cost of a missed default exceeds the cost of a rejected good applicant.

---

## Setup and Installation

### Prerequisites

- Python **3.13+** (see `pyproject.toml`)
- [uv](https://github.com/astral-sh/uv) package manager  
- Supabase project (PostgreSQL + Storage with model artifacts)  
- Optional: [Resend](https://resend.com) for real email (or use `EMAIL_BACKEND=console`)  
- Optional: Docker Desktop for container runs  

### Environment variables

Create a `.env` in the project root. **No spaces around `=`** (required for `docker run --env-file`).

```env
# JWT
SECRET_KEY=your_jwt_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Supabase Postgres (used by SQLAlchemy)
user=your_db_user
password=your_db_password
host=db.your-project.supabase.co
port=5432
dbname=postgres

# Supabase Storage (model download at startup)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_service_role_key

# Email: console | resend
EMAIL_BACKEND=console
RESEND_API_KEY=re_your_resend_api_key

# Optional
PUBLIC_APP_URL=http://127.0.0.1:8000
PASSWORD_RESET_EXPIRE_MINUTES=15
MODEL_VERSION=loan-risk-v1
MONITOR_DEFAULT_DAYS=7
MONITOR_DRIFT_BASELINE_DAYS=30
MONITOR_DRIFT_RECENT_DAYS=7
```

> **Note:** DB vars are separate fields (`user`, `password`, `host`, `port`, `dbname`), not a single `DATABASE_URL`.

### Local install

```bash
git clone https://github.com/Hobim8/loan_backend.git
cd loan_backend
uv venv
uv sync
# or: uv pip install -r requirement.txt
```

### Database setup

```bash
python -m db.create_db
```

If you already had tables before monitoring was added, apply `scripts/migrate_monitoring.sql` (or recreate via `create_db` in a safe environment).

### Run the API (local)

```bash
uvicorn app.main:app --reload
```

| URL | Purpose |
|---|---|
| http://127.0.0.1:8000 | Web UI |
| http://127.0.0.1:8000/docs | Swagger |
| http://127.0.0.1:8000/health | Health |
| http://127.0.0.1:8000/metrics | Prometheus |

---

## Docker

Single service only—no `docker-compose` file. Postgres and model storage remain on Supabase.

```bash
# 1) Build image
docker build -t loan-backend .

# 2) Run with env file
docker run --rm -p 8000:8000 --env-file .env loan-backend
```

Then open http://127.0.0.1:8000 or http://127.0.0.1:8000/docs.

**Notes**
- Rebuild after code or Dockerfile changes: `docker build -t loan-backend .`
- `.env` is not copied into the image (see `.dockerignore`); always pass `--env-file .env`
- Startup needs valid Supabase credentials so the model can download and the DB can connect

---

## Typical usage flow

1. **Sign up** → receive verification code (`console` logs it; Resend emails it)  
2. **Verify email** → account becomes active  
3. **Log in** → receive JWT  
4. **Predict** → `Authorization: Bearer <token>` on `POST /loan/predict`  
5. **Staff monitoring** (staff user) → inspect summary, drift, performance; record outcomes  

Password reset: `POST /auth/forgot-password` → open link from email/logs → set new password on the form or via `POST /auth/reset-password`.

---

## Key Engineering Decisions

**Why CatBoost?** Strong on mixed tabular features with limited tuning; good fit for loan risk datasets with numeric and categorical fields.

**Why a custom threshold (0.25)?** A 0.50 cutoff maximises balanced accuracy. A lower bar increases sensitivity to default risk when missing a default is more costly than a false alarm.

**Why Supabase Storage for models?** Keeps large binary artifacts out of git history, decouples model releases from app deploys, and supports shared model versions across environments.

**Why email verification?** Reduces disposable / abuse accounts before API access.

**Why staff-only monitoring + separate outcomes?** Inference stays available to verified users; operational analytics and ground-truth labeling stay restricted. Outcomes enable real performance metrics after loans resolve.

**Why Prometheus and JSON monitoring?** Prometheus for time-series scrapes and alerts; JSON `/monitoring/*` for product/staff dashboards without requiring a metrics stack to explore the data.

**Why Docker without Compose?** One process to package; managed cloud DB/storage means no local multi-container stack is required for a realistic deploy path.

---

## Author

Victor — Backend and AI/ML Engineer  
GitHub: [Hobim8](https://github.com/Hobim8)
