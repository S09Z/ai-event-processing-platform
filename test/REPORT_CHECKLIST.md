# Test Report Checklist
**Project:** AI Event Processing Platform
**Date:** 2026-04-15
**Prepared for:** Project Manager

---

## Summary

| Suite | File | Total Cases | Status |
|---|---|---|---|
| Middleware Pre-flight | `test/middleware/test_gateway_middleware.py` | 7 | 🟡 Pending run |
| Event Service | `test/functional/test_event_service.py` | 13 | 🟡 Pending run |
| AI Inference | `test/functional/test_inference_service.py` | 5 | 🟡 Pending run |
| **Total** | | **25** | |

---

## 1. Middleware Pre-flight Tests
> **Purpose:** Verify gateway security and routing are correctly wired **before** the app is deployed. These are connection/security smoke tests, not business logic.

### 1.1 Health Endpoint
| # | Test | What it checks | Input | Expected | Pass? |
|---|---|---|---|---|---|
| M-01 | `test_health_returns_ok` | `/health` returns service status | `GET /health` | status=`ok`, service=`gateway`, HTTP 200 | 🟡 |

### 1.2 JWT Authentication
| # | Test | What it checks | Input | Expected | Pass? |
|---|---|---|---|---|---|
| M-02 | `test_request_without_auth_returns_401` | Request with no token is blocked | No `Authorization` header | HTTP **401** | 🟡 |
| M-03 | `test_request_with_invalid_token_returns_401` | Malformed JWT is rejected | `Authorization: Bearer invalid.token.here` | HTTP **401** | 🟡 |
| M-04 | `test_health_is_public` | Public path bypasses auth | `GET /health` (no token) | HTTP **200** (not blocked) | 🟡 |

### 1.3 Correlation ID
| # | Test | What it checks | Input | Expected | Pass? |
|---|---|---|---|---|---|
| M-05 | `test_response_contains_correlation_id` | Every response carries a trace ID | `GET /health` | Header `X-Correlation-ID` exists | 🟡 |
| M-06 | `test_propagates_existing_correlation_id` | Client-supplied trace ID is echoed back | Header `X-Correlation-ID: test-correlation-id-123` | Response header = `test-correlation-id-123` | 🟡 |

---

## 2. Event Service – Functional Tests
> **Purpose:** Verify core business logic for creating, retrieving, and managing events. All DB and Kafka calls are mocked — no real infrastructure needed.

### 2.1 Create Event
| # | Test | What it checks | Input | Expected | Pass? |
|---|---|---|---|---|---|
| F-01 | `test_create_event_returns_event` | Service returns the saved event with correct type | type=`click`, payload=`{button: submit}` | result.type=`click`, status=`PENDING` | 🟡 |
| F-02 | `test_create_event_calls_repo_save` | Repository `save()` is called exactly once | type=`purchase` | `repo.save` called **1 time** | 🟡 |
| F-03 | `test_create_event_publishes_to_kafka` | Event is published to Kafka after save | type=`click` | `kafka.publish_event` called with saved event | 🟡 |
| F-04 | `test_create_event_raises_on_empty_type` | Empty event type is rejected | type=`""` | Raises `ValueError` or `KeyError` | 🟡 |
| F-05 | `test_create_event_uses_empty_payload_by_default` | Missing payload defaults to `{}` | type=`view` (no payload) | result.payload=`{}` | 🟡 |

### 2.2 Get Event
| # | Test | What it checks | Input | Expected | Pass? |
|---|---|---|---|---|---|
| F-06 | `test_get_event_returns_event` | Existing event is returned by ID | id=`abc-123` (exists) | result.id=`abc-123` | 🟡 |
| F-07 | `test_get_event_returns_none_when_not_found` | Missing event returns None (no crash) | id=`nonexistent-id` | result=`None` | 🟡 |

### 2.3 Event Domain Model
| # | Test | What it checks | Input | Expected | Pass? |
|---|---|---|---|---|---|
| F-08 | `test_event_has_pending_status_by_default` | New events start as PENDING | `Event(type="click")` | status=`PENDING` | 🟡 |
| F-09 | `test_mark_processed_changes_status` | Marking processed changes state | `event.mark_processed()` | status=`PROCESSED` | 🟡 |
| F-10 | `test_mark_failed_changes_status` | Marking failed changes state | `event.mark_failed()` | status=`FAILED` | 🟡 |
| F-11 | `test_empty_type_raises_value_error` | Empty type string is an invalid event | type=`""` | Raises `ValueError` matching `non-empty` | 🟡 |
| F-12 | `test_is_terminal_for_processed` | PROCESSED is a final state (no retries) | `mark_processed()` then `is_terminal()` | `True` | 🟡 |
| F-13 | `test_is_not_terminal_for_pending` | PENDING is not a final state (can still process) | `is_terminal()` on new event | `False` | 🟡 |

---

## 3. AI Inference – Functional Tests
> **Purpose:** Verify the AI inference pipeline correctly handles predictions and validates its domain model. The ML model itself is mocked — no GPU or model download needed.

### 3.1 Inference Service
| # | Test | What it checks | Input | Expected | Pass? |
|---|---|---|---|---|---|
| A-01 | `test_infer_returns_prediction` | Inference returns correct event_id, label, score | event_id=`evt-123`, type=`click` | result.event_id=`evt-123`, label=`POSITIVE`, score=`0.98` | 🟡 |
| A-02 | `test_infer_delegates_to_engine` | Service delegates to the inference engine correctly | event_type=`view`, payload=`{}` | `engine.predict` called with `(event_type="view", payload={})` | 🟡 |

### 3.2 Prediction Domain Model
| # | Test | What it checks | Input | Expected | Pass? |
|---|---|---|---|---|---|
| A-03 | `test_prediction_score_must_be_between_0_and_1` | Score out of range is rejected | score=`1.5` | Raises `ValueError` matching `Score` | 🟡 |
| A-04 | `test_prediction_label_cannot_be_empty` | Blank label is an invalid prediction | label=`"  "` (spaces) | Raises `ValueError` matching `label` | 🟡 |
| A-05 | `test_valid_prediction_creation` | Valid prediction is created without error | label=`POSITIVE`, score=`0.95` | result.label=`POSITIVE`, score=`0.95` | 🟡 |

---

## Legend

| Symbol | Meaning |
|---|---|
| ✅ | Passed |
| ❌ | Failed |
| 🟡 | Pending / Not yet run |
