import os
from dotenv import load_dotenv


load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Model monitoring / artifact identity
MODEL_VERSION = os.getenv("MODEL_VERSION", "loan-risk-v1")

# Default lookback windows (days)
MONITOR_DEFAULT_DAYS = int(os.getenv("MONITOR_DEFAULT_DAYS", "7"))
MONITOR_DRIFT_BASELINE_DAYS = int(os.getenv("MONITOR_DRIFT_BASELINE_DAYS", "30"))
MONITOR_DRIFT_RECENT_DAYS = int(os.getenv("MONITOR_DRIFT_RECENT_DAYS", "7"))

# Password reset (link points at this API host by default; override for a real frontend later)
PUBLIC_APP_URL = os.getenv("PUBLIC_APP_URL", "http://127.0.0.1:8000").rstrip("/")
PASSWORD_RESET_EXPIRE_MINUTES = int(os.getenv("PASSWORD_RESET_EXPIRE_MINUTES", "15"))

# Email delivery: "console" (print to server logs, free for local/dev) or "resend" (real email)
# Free Resend is limited — use console while learning, resend only when you need a real inbox test.
EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "console").strip().lower()