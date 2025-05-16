"""
Stream router for real-time agent logs using Server-Sent Events (SSE).
"""

import asyncio
from datetime import datetime
import json
from typing import AsyncGenerator

from fastapi import APIRouter, Depends
from sse_starlette.sse import EventSourceResponse

from api.models.database import get_db
from utils import get_logger

# Initialize router
router = APIRouter(
    prefix="/stream",
    tags=["stream"],
    responses={404: {"description": "Not found"}},
)

# Create logger
logger = get_logger("api.stream")

# Global queue for log messages
log_queue = asyncio.Queue()

# Function to add logs to the queue
async def add_log(agent: str, level: str, message: str) -> None:
    """Add a log message to the queue for streaming."""
    await log_queue.put({
        "ts": datetime.now().isoformat(),
        "agent": agent,
        "level": level,
        "msg": message
    })

async def log_generator() -> AsyncGenerator[str, None]:
    """Generate log messages from the queue."""
    while True:
        # Wait for a log message
        log_data = await log_queue.get()
        
        # Convert to JSON and yield
        yield json.dumps(log_data)

@router.get("")
async def stream_logs():
    """Stream logs as Server-Sent Events (SSE)."""
    logger.info("Client connected to log stream")
    
    return EventSourceResponse(log_generator())

# Helper function to publish a test log (for development/testing)
@router.post("/test")
async def publish_test_log():
    """Publish a test log message."""
    await add_log("TestAgent", "info", f"Test message at {datetime.now().isoformat()}")
    return {"status": "ok"} 