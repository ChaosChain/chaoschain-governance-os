"""
API Gateway Metrics

This module provides Prometheus metrics for the API Gateway.
"""

import time
from prometheus_client import Counter, Histogram, Gauge, generate_latest

# Define metrics
AGENT_REGISTRATIONS = Counter(
    "chaoscore_agent_registrations_total",
    "Total number of agent registrations"
)

ACTIONS_LOGGED = Counter(
    "chaoscore_actions_logged_total",
    "Total number of actions logged",
    ["action_type"]
)

OUTCOMES_RECORDED = Counter(
    "chaoscore_outcomes_recorded_total",
    "Total number of outcomes recorded",
    ["success"]
)

STUDIOS_CREATED = Counter(
    "chaoscore_studios_created_total",
    "Total number of studios created"
)

TASKS_CREATED = Counter(
    "chaoscore_tasks_created_total",
    "Total number of tasks created"
)

REPUTATION_QUERIES = Counter(
    "chaoscore_reputation_queries_total",
    "Total number of reputation queries"
)

REQUEST_LATENCY = Histogram(
    "chaoscore_request_latency_seconds",
    "Request latency in seconds",
    ["endpoint"]
)

ACTIVE_AGENTS = Gauge(
    "chaoscore_active_agents",
    "Number of active agents"
)

# Track request start time for latency calculation
_REQUESTS_IN_PROGRESS = {}

def start_timer(request_id, endpoint):
    """
    Start a timer for a request.
    
    Args:
        request_id: Request ID
        endpoint: API endpoint
    """
    _REQUESTS_IN_PROGRESS[request_id] = {
        "start_time": time.time(),
        "endpoint": endpoint
    }

def end_timer(request_id):
    """
    End a timer for a request.
    
    Args:
        request_id: Request ID
    """
    if request_id in _REQUESTS_IN_PROGRESS:
        latency = time.time() - _REQUESTS_IN_PROGRESS[request_id]["start_time"]
        endpoint = _REQUESTS_IN_PROGRESS[request_id]["endpoint"]
        REQUEST_LATENCY.labels(endpoint=endpoint).observe(latency)
        del _REQUESTS_IN_PROGRESS[request_id]

def get_metrics():
    """
    Get Prometheus metrics.
    
    Returns:
        str: Prometheus metrics in text format
    """
    return generate_latest() 