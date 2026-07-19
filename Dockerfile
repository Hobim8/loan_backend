# Loan Default Risk Prediction API
# FastAPI + CatBoost + PostgreSQL (Supabase)
# Single base image only — no extra Docker images pulled for tooling.

FROM python:3.13-slim-bookworm

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH"

# libgomp: OpenMP runtime used by CatBoost / scientific wheels
# curl: fetch the uv installer (avoids pulling a second Docker image)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        libgomp1 \
    && curl -LsSf https://astral.sh/uv/install.sh | sh \
    && apt-get purge -y curl \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

ENV PATH="/root/.local/bin:$PATH"

# Dependencies first for layer caching (lockfile matches pyproject.toml)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

# App source — model artifacts load from Supabase at runtime, not baked in
COPY app/ ./app/
COPY core/ ./core/
COPY db/ ./db/
COPY ML/ ./ML/
COPY routes/ ./routes/
COPY schemas/ ./schemas/
COPY frontend/ ./frontend/

RUN uv sync --frozen --no-dev

# Secrets / config via -e or --env-file at runtime — never COPY .env
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
