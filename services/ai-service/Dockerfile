# ── Stage 1: Builder ──────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml .
# Install CPU-only torch to keep image size reasonable
RUN uv sync --no-dev --frozen

# ── Stage 2: Production ───────────────────────────────────────────────────────
FROM python:3.11-slim AS production

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

COPY app/ ./app/

RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser
USER appuser

# Pre-download model at build time to avoid cold-start latency
# ARG MODEL_NAME=distilbert-base-uncased-finetuned-sst-2-english
# RUN python -c "from transformers import pipeline; pipeline('text-classification', model='${MODEL_NAME}')"

EXPOSE 8002

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8002/health').raise_for_status()"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]
