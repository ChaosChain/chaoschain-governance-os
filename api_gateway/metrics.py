"""
API Gateway Metrics

This module provides Prometheus metrics for the API Gateway.
"""

import time
import psutil
import threading
from prometheus_client import Counter, Histogram, Gauge, Summary, Info, generate_latest

# System metrics - collected periodically
CPU_USAGE = Gauge(
    "chaoscore_cpu_usage_percent",
    "CPU usage percentage"
)

MEMORY_USAGE = Gauge(
    "chaoscore_memory_usage_bytes",
    "Memory usage in bytes"
)

SYSTEM_INFO = Info(
    "chaoscore_system",
    "System information"
)

# Initialize system info
SYSTEM_INFO.info({
    "version": "0.1.0",
    "python_version": "3.12.8",
    "start_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
})

# Agent metrics
AGENT_REGISTRATIONS = Counter(
    "chaoscore_agent_registrations_total",
    "Total number of agent registrations"
)

ACTIVE_AGENTS = Gauge(
    "chaoscore_active_agents",
    "Number of active agents"
)

# Action metrics
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

# Studio metrics
STUDIOS_CREATED = Counter(
    "chaoscore_studios_created_total",
    "Total number of studios created"
)

TASKS_CREATED = Counter(
    "chaoscore_tasks_created_total",
    "Total number of tasks created"
)

# Reputation metrics
REPUTATION_QUERIES = Counter(
    "chaoscore_reputation_queries_total",
    "Total number of reputation queries"
)

REPUTATION_SCORES = Summary(
    "chaoscore_reputation_scores",
    "Summary of reputation scores",
    ["query_type"]
)

# Authentication metrics
JWT_VALIDATIONS = Counter(
    "chaoscore_jwt_validations_total",
    "Total number of JWT validations",
    ["result"]
)

JWT_KEY_ROTATIONS = Counter(
    "chaoscore_jwt_key_rotations_total",
    "Total number of JWT key rotations"
)

# Request metrics
REQUEST_LATENCY = Histogram(
    "chaoscore_request_latency_seconds",
    "Request latency in seconds",
    ["endpoint", "method"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0)
)

REQUEST_SIZE = Histogram(
    "chaoscore_request_size_bytes",
    "Request size in bytes",
    ["endpoint"],
    buckets=(100, 500, 1000, 5000, 10000, 50000, 100000)
)

RESPONSE_SIZE = Histogram(
    "chaoscore_response_size_bytes",
    "Response size in bytes",
    ["endpoint", "status_code"],
    buckets=(100, 500, 1000, 5000, 10000, 50000, 100000)
)

HTTP_ERRORS = Counter(
    "chaoscore_http_errors_total",
    "Total number of HTTP errors",
    ["endpoint", "status_code"]
)

# Track request start time for latency calculation
_REQUESTS_IN_PROGRESS = {}

def start_timer(request_id, endpoint, method="GET"):
    """
    Start a timer for a request.
    
    Args:
        request_id: Request ID
        endpoint: API endpoint
        method: HTTP method
    """
    _REQUESTS_IN_PROGRESS[request_id] = {
        "start_time": time.time(),
        "endpoint": endpoint,
        "method": method
    }

def end_timer(request_id, response_status=200, request_size=0, response_size=0):
    """
    End a timer for a request.
    
    Args:
        request_id: Request ID
        response_status: HTTP status code
        request_size: Request size in bytes
        response_size: Response size in bytes
    """
    if request_id in _REQUESTS_IN_PROGRESS:
        latency = time.time() - _REQUESTS_IN_PROGRESS[request_id]["start_time"]
        endpoint = _REQUESTS_IN_PROGRESS[request_id]["endpoint"]
        method = _REQUESTS_IN_PROGRESS[request_id]["method"]
        
        # Record request latency
        REQUEST_LATENCY.labels(endpoint=endpoint, method=method).observe(latency)
        
        # Record request/response size if provided
        if request_size > 0:
            REQUEST_SIZE.labels(endpoint=endpoint).observe(request_size)
        
        if response_size > 0:
            RESPONSE_SIZE.labels(endpoint=endpoint, status_code=response_status).observe(response_size)
        
        # Record HTTP errors
        if response_status >= 400:
            HTTP_ERRORS.labels(endpoint=endpoint, status_code=response_status).inc()
        
        del _REQUESTS_IN_PROGRESS[request_id]

def record_reputation_score(score, query_type="agent"):
    """
    Record a reputation score.
    
    Args:
        score: Reputation score (0.0-1.0)
        query_type: Type of reputation query
    """
    REPUTATION_SCORES.labels(query_type=query_type).observe(score)

def record_jwt_validation(success=True):
    """
    Record a JWT validation.
    
    Args:
        success: Whether the validation was successful
    """
    result = "success" if success else "failure"
    JWT_VALIDATIONS.labels(result=result).inc()

def record_jwt_key_rotation():
    """
    Record a JWT key rotation.
    """
    JWT_KEY_ROTATIONS.inc()

# System metrics collection
def collect_system_metrics():
    """
    Collect system metrics periodically.
    """
    while True:
        try:
            # Update CPU usage (as percentage)
            CPU_USAGE.set(psutil.cpu_percent())
            
            # Update memory usage (in bytes)
            memory = psutil.virtual_memory()
            MEMORY_USAGE.set(memory.used)
            
            # Sleep for 5 seconds before collecting again
            time.sleep(5)
        except Exception as e:
            # Log error but don't crash the thread
            print(f"Error collecting system metrics: {e}")
            time.sleep(10)

# Start system metrics collection in a background thread
system_metrics_thread = threading.Thread(target=collect_system_metrics, daemon=True)
system_metrics_thread.start()

def get_metrics():
    """
    Get Prometheus metrics.
    
    Returns:
        str: Prometheus metrics in text format
    """
    return generate_latest() 