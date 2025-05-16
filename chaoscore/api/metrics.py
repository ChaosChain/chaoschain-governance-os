"""
Metrics API for ChaosCore

This module provides the metrics API for ChaosCore.
"""

import os
import time
import logging
from typing import Dict, Any
from fastapi import APIRouter, Depends, Request
from prometheus_client import (
    Counter, Gauge, Histogram, REGISTRY,
    generate_latest, CONTENT_TYPE_LATEST
)
from starlette.responses import Response

from chaoscore.core.database_adapter import PostgreSQLAdapter

logger = logging.getLogger(__name__)

# Define metrics
AGENT_REGISTRATIONS = Counter(
    'chaoscore_agent_registrations_total',
    'Total number of agent registrations'
)
ACTION_LOGS = Counter(
    'chaoscore_actions_total',
    'Total number of logged actions',
    ['action_type']
)
SIMULATION_RUNS = Counter(
    'chaoscore_simulations_total',
    'Total number of simulation runs'
)
ANCHORING_OPERATIONS = Counter(
    'chaoscore_anchoring_operations_total',
    'Total number of blockchain anchoring operations'
)
AGENT_COUNT = Gauge(
    'chaoscore_agents_total',
    'Total number of registered agents'
)
API_REQUEST_DURATION = Histogram(
    'chaoscore_api_request_duration_seconds',
    'API request duration in seconds',
    ['endpoint', 'method']
)
ACTIVE_REQUESTS = Gauge(
    'chaoscore_active_requests',
    'Number of active API requests',
    ['endpoint']
)

# Create router
router = APIRouter(tags=["Metrics"])


def sync_metrics_from_db():
    """
    Sync metrics from the database.
    """
    if os.environ.get("CHAOSCORE_ENV", "") in ("staging", "production"):
        try:
            db = PostgreSQLAdapter()
            
            # Get agent count
            result = db.execute(
                "SELECT value FROM metrics WHERE name = 'agent_count'",
                fetch='one'
            )
            if result:
                AGENT_COUNT.set(result['value'])
            
            # Get action count
            result = db.execute(
                "SELECT value FROM metrics WHERE name = 'action_count'",
                fetch='one'
            )
            if result:
                ACTION_LOGS.labels(action_type='all')._value.set(result['value'])
            
            # Get simulation count
            result = db.execute(
                "SELECT value FROM metrics WHERE name = 'simulation_count'",
                fetch='one'
            )
            if result:
                SIMULATION_RUNS._value.set(result['value'])
            
            # Get anchoring count
            result = db.execute(
                "SELECT value FROM metrics WHERE name = 'anchoring_count'",
                fetch='one'
            )
            if result:
                ANCHORING_OPERATIONS._value.set(result['value'])
        except Exception as e:
            logger.error(f"Error syncing metrics from DB: {e}")


@router.get("/metrics")
async def metrics():
    """
    Get Prometheus metrics.
    """
    # Sync metrics from the database
    sync_metrics_from_db()
    
    # Generate metrics
    content = generate_latest(REGISTRY)
    return Response(content=content, media_type=CONTENT_TYPE_LATEST)


class MetricsMiddleware:
    """
    Middleware to collect API metrics.
    """
    
    async def __call__(self, request: Request, call_next):
        """
        Process the request and collect metrics.
        
        Args:
            request: FastAPI request
            call_next: Next middleware
            
        Returns:
            Response
        """
        endpoint = request.url.path
        method = request.method
        
        # Track active requests
        ACTIVE_REQUESTS.labels(endpoint=endpoint).inc()
        
        # Track request duration
        start_time = time.time()
        try:
            response = await call_next(request)
            return response
        finally:
            # Record request duration
            duration = time.time() - start_time
            API_REQUEST_DURATION.labels(
                endpoint=endpoint,
                method=method
            ).observe(duration)
            
            # Decrement active requests
            ACTIVE_REQUESTS.labels(endpoint=endpoint).dec()


def register_metrics_events(app):
    """
    Register metrics events with the FastAPI app.
    
    Args:
        app: FastAPI app
    """
    @app.on_event("startup")
    async def startup_metrics():
        """Startup event handler."""
        # Add metrics middleware
        app.middleware("http")(MetricsMiddleware())
        
        # Sync metrics from the database
        sync_metrics_from_db()


def increment_agent_registration():
    """Increment agent registration counter."""
    AGENT_REGISTRATIONS.inc()


def increment_action_log(action_type):
    """
    Increment action log counter.
    
    Args:
        action_type: Type of action
    """
    ACTION_LOGS.labels(action_type=action_type).inc()
    ACTION_LOGS.labels(action_type='all').inc()


def increment_simulation_run():
    """Increment simulation run counter."""
    SIMULATION_RUNS.inc()


def increment_anchoring_operation():
    """Increment anchoring operation counter."""
    ANCHORING_OPERATIONS.inc() 