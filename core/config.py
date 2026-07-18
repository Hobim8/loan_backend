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