# AI Event Processing Platform

## Workflow

```
Client
  │
  ▼
┌─────────────────────────────────────────┐
│  Gateway  :8000                         │
│  • JWT / API Key authentication         │
│  • Redis-backed rate limiting           │
│  • Correlation ID injection             │
└────────────────┬────────────────────────┘
                 │ validated request
                 ▼
┌─────────────────────────────────────────┐
│  Event Service  :8001                   │
│  POST /api/v1/events                    │
│  • Validates payload (Pydantic)         │
│  • Persists event → PostgreSQL          │
│  • Publishes event → Kafka (events)     │
└────────────┬────────────────────────────┘
             │ Kafka topic: events
             ▼
┌─────────────────────────────────────────┐
│  AI Service  :8002                      │
│  Kafka Worker (background)              │
│  • Consumes events topic                │
│  • Runs ML inference (DistilBERT)       │
│  • Publishes prediction → Kafka         │
│    (ai-results)                         │
│  • Failed messages → DLQ (events-dlq)  │
│                                         │
│  POST /api/v1/ai/infer  (sync path)     │
└────────────┬────────────────────────────┘
             │ Kafka topic: ai-results
             ▼
┌─────────────────────────────────────────┐
│  Analytics Service                      │
│  • Consumes ai-results                  │
│  • Aggregates metrics                   │
│  • Exposes Prometheus endpoint          │
└─────────────────────────────────────────┘
```

### Async vs Sync inference

| Path | Description |
|------|-------------|
| **Async** (default) | Client posts to Event Service → Kafka → AI Worker processes in background |
| **Sync** | Client posts directly to `POST /api/v1/ai/infer` on AI Service |

### Infrastructure

| Service | Role |
|---------|------|
| PostgreSQL | Event persistence |
| Redis | Rate-limit counters, caching |
| Kafka | Event streaming between services |
| Prometheus | Metrics scraping |
| OpenTelemetry | Distributed tracing (Correlation ID) |

### Running locally

```zsh
# 1. Start infrastructure
docker compose --profile dev up -d

# 2. Sync dependencies (uv workspace – single .venv at root)
uv sync

# 3. Start services (each in a separate terminal, from repo root)
PYTHONPATH=services/gateway      uv run python -m uvicorn app.main:app --port 8000 --reload
PYTHONPATH=services/event-service uv run python -m uvicorn app.main:app --port 8001 --reload
PYTHONPATH=services/ai-service    uv run python -m uvicorn app.main:app --port 8002 --reload
```

### API Docs (development only)

| Service | Swagger UI | ReDoc |
|---------|-----------|-------|
| Gateway | http://localhost:8000/docs | http://localhost:8000/redoc |
| Event Service | http://localhost:8001/docs | http://localhost:8001/redoc |
| AI Service | http://localhost:8002/docs | http://localhost:8002/redoc |

### Running tests

```zsh
# Connection smoke tests
uv run pytest test/test_connections.py -v

# Unit tests per service
uv run pytest services/event-service/tests -v
uv run pytest services/ai-service/tests -v

# Functional / middleware tests
uv run pytest test/ -v
```
