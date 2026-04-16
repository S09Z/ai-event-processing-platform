"""
Connection smoke tests for PostgreSQL, Redis, and Kafka.
Run with: pytest test/test_connections.py -v
"""

import os

import pytest
from dotenv import load_dotenv

load_dotenv()

POSTGRES_URL = os.getenv("DATABASE_URL", "").replace("+asyncpg", "")  # use sync driver
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")


# ─── PostgreSQL ───────────────────────────────────────────────────────────────


def test_postgres_connection() -> None:
    """Verify a basic SELECT 1 succeeds against PostgreSQL."""
    import psycopg2  # type: ignore[import]

    host = os.getenv("POSTGRES_HOST", "localhost")
    port = int(os.getenv("POSTGRES_PORT", "5432"))
    db = os.getenv("POSTGRES_DB", "events_db")
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "postgres")

    conn = psycopg2.connect(
        host=host, port=port, dbname=db, user=user, password=password
    )
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
            result = cur.fetchone()
        assert result == (1,), f"Unexpected result: {result}"
    finally:
        conn.close()


# ─── Redis ────────────────────────────────────────────────────────────────────


def test_redis_connection() -> None:
    """Verify PING/PONG against Redis."""
    import redis  # type: ignore[import]

    client = redis.from_url(REDIS_URL, socket_connect_timeout=3)
    try:
        response = client.ping()
        assert response is True, "Redis did not respond with PONG"
    finally:
        client.close()


def test_redis_set_get() -> None:
    """Verify basic SET/GET round-trip."""
    import redis  # type: ignore[import]

    client = redis.from_url(REDIS_URL, socket_connect_timeout=3)
    try:
        client.set("__smoke_test__", "ok", ex=5)
        value = client.get("__smoke_test__")
        assert value == b"ok", f"Unexpected value: {value}"
    finally:
        client.delete("__smoke_test__")
        client.close()


# ─── Kafka ────────────────────────────────────────────────────────────────────


def test_kafka_connection() -> None:
    """Verify Kafka broker is reachable by listing topics."""
    from kafka import KafkaAdminClient  # type: ignore[import]
    from kafka.errors import NoBrokersAvailable  # type: ignore[import]

    try:
        admin = KafkaAdminClient(
            bootstrap_servers=KAFKA_BOOTSTRAP,
            client_id="smoke-test",
            request_timeout_ms=5000,
        )
        topics = admin.list_topics()
        admin.close()
        assert isinstance(topics, list), "Expected a list of topics"
    except NoBrokersAvailable as exc:
        pytest.fail(f"No Kafka brokers available at {KAFKA_BOOTSTRAP}: {exc}")


def test_kafka_produce_consume() -> None:
    """Verify a message can be produced and consumed on the events topic."""
    import uuid

    from kafka import KafkaConsumer, KafkaProducer  # type: ignore[import]
    from kafka.errors import NoBrokersAvailable  # type: ignore[import]

    topic = os.getenv("KAFKA_EVENTS_TOPIC", "events")
    payload = f"smoke-{uuid.uuid4()}".encode()

    try:
        # Start consumer first (auto_offset_reset="earliest" so it won't miss
        # messages produced while it is still initialising its partition assignment)
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=KAFKA_BOOTSTRAP,
            auto_offset_reset="earliest",
            consumer_timeout_ms=8000,
            group_id=None,
        )
        # Trigger partition assignment before producing
        consumer.poll(timeout_ms=1000)

        producer = KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP, request_timeout_ms=5000
        )
        future = producer.send(topic, value=payload)
        future.get(timeout=5)  # wait for broker ack
        producer.close()

        received = []
        for msg in consumer:
            if msg.value == payload:
                received.append(msg.value)
                break
        consumer.close()

        assert payload in received, "Produced message not received within timeout"
    except NoBrokersAvailable as exc:
        pytest.fail(f"No Kafka brokers available at {KAFKA_BOOTSTRAP}: {exc}")
