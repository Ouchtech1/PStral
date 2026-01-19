"""
Prometheus metrics for Pstral.
Provides observability into application performance.
"""
from prometheus_client import Counter, Histogram, Gauge, Info
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
import time

# Application info
APP_INFO = Info('pstral', 'Pstral application information')
APP_INFO.info({
    'version': '1.0.0',
    'name': 'Pstral AI Assistant',
    'company': 'Pack Solutions'
})

# Request metrics
REQUEST_COUNT = Counter(
    'pstral_requests_total',
    'Total number of HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'pstral_request_latency_seconds',
    'Request latency in seconds',
    ['method', 'endpoint'],
    buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

# Chat metrics
CHAT_REQUESTS = Counter(
    'pstral_chat_requests_total',
    'Total number of chat requests',
    ['mode']
)

CHAT_LATENCY = Histogram(
    'pstral_chat_latency_seconds',
    'Chat response latency in seconds',
    ['mode'],
    buckets=[1.0, 5.0, 10.0, 30.0, 60.0, 120.0]
)

CHAT_TOKENS = Counter(
    'pstral_chat_tokens_total',
    'Total tokens generated',
    ['mode']
)

# Active sessions
ACTIVE_SESSIONS = Gauge(
    'pstral_active_sessions',
    'Number of active user sessions'
)

# SQL execution metrics
SQL_EXECUTIONS = Counter(
    'pstral_sql_executions_total',
    'Total SQL queries executed',
    ['status']
)

# User metrics
USERS_TOTAL = Gauge(
    'pstral_users_total',
    'Total number of registered users'
)

LOGIN_ATTEMPTS = Counter(
    'pstral_login_attempts_total',
    'Total login attempts',
    ['status']
)

# Database metrics
DB_CONNECTIONS = Gauge(
    'pstral_db_connections',
    'Number of database connections',
    ['database']
)


def get_metrics() -> Response:
    """Generate Prometheus metrics response."""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


def record_request(method: str, endpoint: str, status: int, duration: float):
    """Record a request for metrics."""
    REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=str(status)).inc()
    REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(duration)


def record_chat(mode: str, duration: float, tokens: int = 0):
    """Record a chat request for metrics."""
    CHAT_REQUESTS.labels(mode=mode).inc()
    CHAT_LATENCY.labels(mode=mode).observe(duration)
    if tokens > 0:
        CHAT_TOKENS.labels(mode=mode).inc(tokens)


def record_sql_execution(success: bool):
    """Record a SQL execution for metrics."""
    status = "success" if success else "error"
    SQL_EXECUTIONS.labels(status=status).inc()


def record_login(success: bool):
    """Record a login attempt for metrics."""
    status = "success" if success else "failure"
    LOGIN_ATTEMPTS.labels(status=status).inc()

