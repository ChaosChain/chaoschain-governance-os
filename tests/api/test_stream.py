"""
Unit tests for the streaming endpoint.
"""

import pytest
import asyncio
from httpx import AsyncClient
import json
from fastapi import FastAPI
from sse_starlette.sse import EventSourceResponse

# Import to patch
import sys
import os

# Add the parent directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from api.rest.routers import stream
from api.rest.app import app

@pytest.mark.asyncio
async def test_stream_test_endpoint():
    """Test the test endpoint for publishing logs."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/stream/test")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

@pytest.mark.asyncio
async def test_stream_add_log():
    """Test adding logs to the queue."""
    # Clear the queue first to ensure clean test
    while not stream.log_queue.empty():
        await stream.log_queue.get()
    
    # Add a test log
    await stream.add_log("TestAgent", "info", "Test message")
    
    # Verify the log was added to the queue
    assert not stream.log_queue.empty()
    log = await stream.log_queue.get()
    assert log["agent"] == "TestAgent"
    assert log["level"] == "info"
    assert log["msg"] == "Test message"
    assert "ts" in log

@pytest.mark.asyncio
async def test_log_generator():
    """Test the log generator function."""
    # Clear the queue first
    while not stream.log_queue.empty():
        await stream.log_queue.get()
    
    # Add a test log
    test_log = {"ts": "2023-01-01T00:00:00", "agent": "TestAgent", "level": "info", "msg": "Test message"}
    await stream.log_queue.put(test_log)
    
    # Get a generator
    generator = stream.log_generator()
    
    # Get the first item from the generator
    item = await anext(generator)
    
    # Verify the item is the JSON serialized log
    assert item == json.dumps(test_log)

# Mock for EventSourceResponse to make testing easier
class MockEventSourceResponse:
    def __init__(self, generator):
        self.generator = generator
        
    async def get_first_item(self):
        return await anext(self.generator)

# Patch EventSourceResponse for testing
@pytest.fixture(autouse=True)
def patch_sse(monkeypatch):
    original_sse = stream.EventSourceResponse
    
    def mock_sse(generator):
        return MockEventSourceResponse(generator)
    
    monkeypatch.setattr(stream, 'EventSourceResponse', mock_sse)
    yield
    monkeypatch.setattr(stream, 'EventSourceResponse', original_sse)

@pytest.mark.asyncio
async def test_stream_logs_endpoint():
    """Test the stream logs endpoint."""
    # Clear the queue first
    while not stream.log_queue.empty():
        await stream.log_queue.get()
    
    # Add a test log
    test_log = {"ts": "2023-01-01T00:00:00", "agent": "TestAgent", "level": "info", "msg": "Test message"}
    await stream.log_queue.put(test_log)
    
    # Test the endpoint directly
    response = await stream.stream_logs()
    
    # Verify the response is a MockEventSourceResponse with our generator
    assert isinstance(response, MockEventSourceResponse)
    
    # Get the first item from the generator
    item = await response.get_first_item()
    
    # Verify the item is the JSON serialized log
    assert item == json.dumps(test_log) 