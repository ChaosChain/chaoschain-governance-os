"""
Streaming log endpoint using Server-Sent Events (SSE).
"""

import asyncio
from datetime import datetime
import json
from typing import Optional

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
import logging

router = APIRouter(prefix="/stream", tags=["stream"])

# Global queue for log messages
log_queue = asyncio.Queue()

# Function to add log messages to the queue
async def add_log_message(agent: str, level: str, msg: str):
    """Add a log message to the queue."""
    await log_queue.put({
        "ts": datetime.now().isoformat(),
        "agent": agent,
        "level": level,
        "msg": msg
    })

class StreamHandler(logging.Handler):
    """Logging handler that sends logs to the SSE stream."""
    
    def emit(self, record):
        """Emit a log record to the stream."""
        try:
            # Extract agent name if available
            agent = getattr(record, "agent", "System")
            
            # Format the message
            msg = self.format(record)
            
            # Use asyncio to add to queue
            asyncio.run_coroutine_threadsafe(
                add_log_message(agent, record.levelname.lower(), msg),
                asyncio.get_event_loop()
            )
        except Exception:
            self.handleError(record)

@router.get("")
async def stream_logs(request: Request):
    """
    Stream logs as Server-Sent Events (SSE).
    
    Connect to this endpoint using an EventSource in JavaScript.
    """
    async def event_generator():
        while True:
            # Check if client is still connected
            if await request.is_disconnected():
                break
                
            try:
                # Wait for a log message with timeout
                message = await asyncio.wait_for(log_queue.get(), timeout=1.0)
                
                # Convert to JSON and send
                yield f"data: {json.dumps(message)}\n\n"
            except asyncio.TimeoutError:
                # Send a keep-alive comment every second if no messages
                yield ": keep-alive\n\n"
            except Exception as e:
                logging.error(f"Error in SSE stream: {str(e)}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
                break
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable buffering in Nginx
        }
    )

# Initialize handler when module is loaded
def initialize_stream_handler():
    """Add the stream handler to the root logger."""
    handler = StreamHandler()
    handler.setLevel(logging.INFO)
    logging.getLogger().addHandler(handler)

# Only initialize in production, not during tests
import os
if os.getenv("ENABLE_STREAM", "0") == "1":
    initialize_stream_handler() 