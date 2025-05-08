"""Tests for the streaming API endpoint."""

import asyncio
import json
import pytest
import pytest_asyncio
from httpx import AsyncClient
from fastapi import FastAPI
from api.rest.app import app as fastapi_app
from api.rest.routers.stream import add_log_message

@pytest.mark.asyncio
async def test_stream_endpoint_returns_sse():
    """Test that the stream endpoint returns SSE data."""
    async with AsyncClient(app=fastapi_app, base_url="http://test") as client:
        # Start listening to the stream in the background
        response = await client.get("/stream", timeout=None)
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream"
        
        # The response should have a streaming body
        assert hasattr(response, "aiter_raw")
        
        # Check if we get a keep-alive message
        # This is needed since the first event is likely to be a keep-alive
        async def read_first_event():
            buffer = b""
            async for chunk in response.aiter_raw():
                buffer += chunk
                if b"\n\n" in buffer:  # End of SSE event
                    return buffer.decode("utf-8")
            return ""
            
        first_event = await asyncio.wait_for(read_first_event(), timeout=2)
        assert ": keep-alive" in first_event or "data:" in first_event

@pytest.mark.asyncio
async def test_stream_receives_log_messages():
    """Test that log messages sent to the queue appear in the stream."""
    async with AsyncClient(app=fastapi_app, base_url="http://test") as client:
        # Start listening to the stream in the background
        response_task = asyncio.create_task(
            client.get("/stream", timeout=None)
        )
        
        # Give the stream time to establish
        await asyncio.sleep(0.5)
        
        # Send a test message to the queue
        test_message = {
            "agent": "Test Agent",
            "level": "info",
            "msg": "Test message"
        }
        await add_log_message(**test_message)
        
        # Read from the stream
        response = await response_task
        
        # Get the first data chunk
        async def read_data_event():
            buffer = b""
            async for chunk in response.aiter_raw():
                buffer += chunk
                if b"data:" in buffer and b"\n\n" in buffer:
                    return buffer.decode("utf-8")
            return ""
        
        event_data = await asyncio.wait_for(read_data_event(), timeout=2)
        
        # Extract and parse the JSON data
        data_line = next((line for line in event_data.splitlines() if line.startswith("data:")), None)
        assert data_line is not None
        
        json_data = json.loads(data_line.replace("data: ", ""))
        
        # Check the message content
        assert json_data["agent"] == test_message["agent"]
        assert json_data["level"] == test_message["level"]
        assert json_data["msg"] == test_message["msg"]
        assert "ts" in json_data  # Timestamp should be added 