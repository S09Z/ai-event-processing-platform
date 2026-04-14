# ── Stage 1: Builder ──────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml .
RUN uv sync --no-dev --frozen

# ── Stage 2: Production ───────────────────────────────────────────────────────
FROM python:3.11-slim AS production

WORKDIR /app

# Copy only the virtual environment from the builder (no dev deps)
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

COPY app/ ./app/

# Non-root user for security
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health').raise_for_status()"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
