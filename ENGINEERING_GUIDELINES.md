# 🚀 AI Event Processing Platform – Engineering Instrument

## 🧠 Purpose

This document defines architecture, coding standards, and development workflow
for a production-grade **AI-powered event processing platform**.

This file is optimized for:

* GitHub Copilot / Cursor / Windsurf
* Clean Architecture
* TDD workflow
* OOP design

---

# 🏗️ System Architecture

## High-Level Flow

```
Client
  ↓
Gateway (Auth, Rate Limit)
  ↓
Reverse Proxy (Routing, Load Balance)
  ↓
FastAPI Services
  ↓
Kafka → Worker → AI Processing → Database
```

---

# 🧩 Components

## 1. Gateway Layer

Responsibilities:

* Authentication (JWT / API Key)
* Rate limiting (Redis)
* Request validation (basic)
* Logging / tracing

Rules:

* ❌ NO business logic
* ✅ Only cross-cutting concerns

---

## 2. Reverse Proxy Layer

Responsibilities:

* Routing
* Load balancing
* TLS termination

Routing Example:

```
/api/events     → event-service
/api/ai         → ai-service
/api/metrics    → analytics-service
```

---

## 3. FastAPI Services

Each service follows:

```
Controller → Service → Domain → Repository
```

---

# 🧱 Clean Architecture Rules (STRICT)

## Layers

### API Layer

* Handles HTTP
* Uses Pydantic schemas
* Calls services only

### Service Layer

* Business logic
* Orchestrates domain objects
* No DB queries directly

### Domain Layer

* Pure OOP
* No framework dependency

### Infrastructure Layer

* DB, Kafka, Redis
* Implements repository interfaces

---

# 🧪 TDD Workflow (MANDATORY)

## Development Loop

1. Write test
2. Run → FAIL
3. Implement minimal code
4. Refactor

---

## Test Structure

```
tests/
 ├── unit/
 ├── integration/
 └── e2e/
```

---

## Example Test

```python
def test_create_event():
    service = EventService(mock_repo)

    result = service.create_event({"type": "click"})

    assert result.type == "click"
```

---

# 🧠 OOP Design Principles

## MUST FOLLOW

* Single Responsibility Principle
* Dependency Injection
* Interface-based design

---

## Example

```python
class EventService:
    def __init__(self, repo: EventRepository):
        self.repo = repo

    def create_event(self, data):
        event = Event(type=data["type"])
        return self.repo.save(event)
```

---

# ⚙️ Tech Stack

## Core

* FastAPI
* Uvicorn
* PostgreSQL
* Redis
* Kafka

## ORM

* SQLAlchemy / SQLModel

## AI

* PyTorch / Transformers

## Tooling

* uv (package manager)
* pytest
* ruff
* mypy

---

# 📦 Package Management (UV)

## Install

```bash
uv init
uv add fastapi uvicorn sqlalchemy asyncpg
uv add pytest pytest-asyncio httpx
```

## Run

```bash
uv run uvicorn app.main:app --reload
```

---

# 🔐 Security Guidelines

* JWT validation at Gateway
* No secrets in code
* Input validation via Pydantic
* Rate limit all public endpoints

---

# ⚡ Performance Rules

* Use async everywhere
* Avoid blocking I/O
* Use connection pooling
* Cache frequently accessed data (Redis)

---

# 📊 Observability

* Structured logging (JSON)
* Correlation ID per request
* Metrics (Prometheus)
* Tracing (OpenTelemetry)

---

# 🔄 Event Processing

## Flow

```
API → Kafka → Worker → AI → DB
```

## Rules

* Events must be idempotent
* Use retry mechanism
* Use dead-letter queue

---

# 🧠 AI Module

* Stateless design
* Version models
* Separate inference from API

---

# 🐳 Docker Guidelines

* One service per container
* Use multi-stage builds
* No dev dependencies in production image

---

# 🔁 CI/CD Requirements

Pipeline must:

* Run tests
* Lint (ruff)
* Type check (mypy)
* Build Docker image

---

# 🚫 Anti-Patterns (DO NOT DO)

* ❌ Business logic in controllers
* ❌ Direct DB access in API layer
* ❌ Shared mutable state
* ❌ Skipping tests

---

# 🎯 Naming Conventions

| Type       | Format           |
| ---------- | ---------------- |
| Service    | EventService     |
| Repository | EventRepository  |
| File       | event_service.py |
| Endpoint   | /api/v1/events   |

---

# 🤖 Copilot Optimization

## Always include docstrings

```python
class EventService:
    """
    Handles business logic for event processing.

    Responsibilities:
    - Validate input
    - Persist event
    - Publish to Kafka
    """
```

---

# 🚀 Future Extensions

* RBAC system
* Billing / quota system
* Feature flags
* Multi-tenant architecture

---

# ✅ Definition of Done

Feature is complete when:

* Tests pass
* Code is linted
* Types are valid
* Endpoint documented
* Logs included
* Error handling implemented

```
```
