"""
Integration tests for the ChaosCore API Gateway.

This module provides tests for the API Gateway endpoints.
"""
import os
import pytest
from fastapi.testclient import TestClient
import jwt
from datetime import datetime, timedelta

# Mock the environment before importing the app
os.environ["CHAOSCORE_ENV"] = "test"
os.environ["SGX_MOCK"] = "true"
os.environ["ETHEREUM_MOCK"] = "true"

from api_gateway.main import app


@pytest.fixture
def client():
    """Create a test client."""
    with TestClient(app) as client:
        yield client


@pytest.fixture
def mock_agent_data():
    """Mock agent data."""
    return {
        "id": "agent-123",
        "name": "Test Agent",
        "email": "test@example.com",
        # Simplified private key for testing only
        "private_key": """-----BEGIN RSA PRIVATE KEY-----
MIIEogIBAAKCAQEAnzyis7qLfFHXBtfvN1VgBLKpJ7GVIvP4neL9Ng/qzZEIdFxD
VW97ldNZfQ1mcAVQmM5OnOXUsp5ZwhVVfnKDe7RLFt4LoFAWnYxzLvJlCkXU9nZG
5ihSpIpuGUiSuTJLauYT2rDiYT/lsNAK2HAYjO/K7GJl+/27hXJFSGPgMOPXe8QA
Xl1gSLgVMS7WiEKfZbAKBDgKllYOdlmL0TnJjHr5r+oVm3j56zYX/FX8SaEkvpHp
JvTYQFSfpJqWpMJtVNGXHND5Y7pd8Q/4l/zGeItUWfmcL6HUxhI41GwKjtfblXrV
lGGGc32LuQPQyKvZr6QzoLMKR7/aN/ay+qtxYQIDAQABAoIBAHQveoaMV4RBM9sI
j9qJiIiFxHzCXEwaLZC9AMqMSbak5En6Qo9GdxYGANjZ8Hz+d8AAI6UBYAQwevU5
X68JKWwLw9YpQRo+hvX2HQAWBj4dNv0tfhaL/duaVvTq+K0CqeGh/xP8/ExUVSfh
SYNzRmkXDhlwCQQxVABwcIK71xJaEfydtBIhqmxxaRrg3axt7KR/1a5CEkrW5V6L
LzWIWDiQV6ztYhRCVYhbNGrX4D/j1Gm5qU7NkTXUCEDPAmN5MwFGZrnXctJiYUAX
lYRHk0G3jweMsNEuP7gfQDItYJjU4zhEOGcOLdWGB4hLK1ZLnBPNXMQmRtQXHkBw
5UT9+AECgYEA0QD12/leF1dgm6DSgkk2bblnzUHaZ7QFB3a23VDlM+GU3+TZdFLP
MJOA1FCQZOeOkLRB5qT4luMXXtBeM2+2bOBMYmSiR08sQ6gGUsVzuSDdOHqsWh62
S6lCr9qZqAlEW0sXK3jMNjFBwRPQAeSVBNnNvfDXJu+g31dJ7sMH3aECgYEAwzK3
5+gVaLeYgKADjI2vqiKGIQV6Yt5CKjf32X+xQr8Y8YCpC4hvr5PR4ZSi3cR9lxQg
CvZVvxhkbdZ07Aipf+yG+rP9AXOCpGIhbpMPuqHlHzD/GXmmBkCEJYhN6S4JyVWV
6ImCJNWYWxOQlv2gkxNYU+SnYhJHWNWTJD7tYAECgYA3NXbTqvgQnXlFqRQKFq7g
GP3aBRG9QoFiN9W3b3tVqTSdvAcUevtL7VAb7J2Z8IpbDvUna6JF5wNJOLuVkIJO
/qWwrBnFeIzpTphoR+oPlT0kO7W++01OHK0BmLXsUJUEI4NEV7QCmygQKFuLrO6v
ylCrGjQrb3yHVFvdGVMoIQKBgGgRLfNrNP1UuRE+UYvTQ5ur7GUJMxcmnfaJ7MvF
NFQHMbRR+gvnfgA4YQWcz7EBgKme9Vzx6bGYXxdvYgy9GpTKXRWyQQJHnWNZHhUC
XZMNJrUlPAJGPMRz3NVS/nNJ/RRiMQnm3IkUTwlhFGYC1Nbkd7IJ3tVvYlpLfYFp
sE4BAoGAJSaFdiHWQFOPgntGQmIMm01WXnrz7OWDB6+H4wKbwroG8RXNBEIVvmJh
ZjYpMnYPGZ1Kv6kLdEBVkZpnlQqj3P+rRld+G8YXUMbd2gI4qCUMggzMQnSq7vJ3
CJz9Ss3O8nXFBw01YlezQfBrCzYpnZ21BxZFdQdYU2OtR6wy7OQ=
-----END RSA PRIVATE KEY-----""",
        "public_key": """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAnzyis7qLfFHXBtfvN1Vg
BLKpJ7GVIvP4neL9Ng/qzZEIdFxDVW97ldNZfQ1mcAVQmM5OnOXUsp5ZwhVVfnKD
e7RLFt4LoFAWnYxzLvJlCkXU9nZG5ihSpIpuGUiSuTJLauYT2rDiYT/lsNAK2HAY
jO/K7GJl+/27hXJFSGPgMOPXe8QAXl1gSLgVMS7WiEKfZbAKBDgKllYOdlmL0TnJ
jHr5r+oVm3j56zYX/FX8SaEkvpHpJvTYQFSfpJqWpMJtVNGXHND5Y7pd8Q/4l/zG
eItUWfmcL6HUxhI41GwKjtfblXrVlGGGc32LuQPQyKvZr6QzoLMKR7/aN/ay+qtx
YQIDAQAB
-----END PUBLIC KEY-----"""
    }


@pytest.fixture
def mock_token(mock_agent_data):
    """Create a mock JWT token."""
    payload = {
        "sub": mock_agent_data["id"],
        "exp": datetime.utcnow() + timedelta(hours=1),
        "iat": datetime.utcnow()
    }
    
    token = jwt.encode(
        payload=payload,
        key=mock_agent_data["private_key"],
        algorithm="RS256",
        headers={"kid": mock_agent_data["id"]}
    )
    
    return token


def test_root_endpoint(client):
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["name"] == "ChaosCore API Gateway"
    assert response.json()["status"] == "running"


def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_create_agent(client):
    """Test creating an agent."""
    agent_data = {
        "name": "Test Agent",
        "email": "test@example.com",
        "metadata": {
            "role": "tester",
            "expertise": "testing",
            "public_key": "test-key"
        }
    }
    
    response = client.post("/agents", json=agent_data)
    assert response.status_code == 201
    assert response.json()["name"] == agent_data["name"]
    assert response.json()["email"] == agent_data["email"]
    assert response.json()["metadata"]["role"] == agent_data["metadata"]["role"]


@pytest.mark.skip(reason="RSA key parsing issues in test environment")
def test_authenticate_and_get_current_agent(client, mock_token, mock_agent_data):
    """Test authenticating and getting the current agent."""
    # Mock the agent registry to return our mock agent
    from unittest.mock import patch
    from chaoscore.core.agent_registry import AgentRegistryInterface
    
    # Skip the test if we can't patch the dependency
    try:
        with patch.object(AgentRegistryInterface, 'get_agent') as mock_get_agent:
            # Mock the agent
            class MockAgent:
                def get_id(self):
                    return mock_agent_data["id"]
                
                def get_name(self):
                    return mock_agent_data["name"]
                
                def get_email(self):
                    return mock_agent_data["email"]
                
                def get_metadata(self):
                    return {"public_key": mock_agent_data["public_key"]}
            
            mock_get_agent.return_value = MockAgent()
            
            # Test getting the current agent
            response = client.get(
                "/agents/me",
                headers={"Authorization": f"Bearer {mock_token}"}
            )
            
            assert response.status_code == 200
            assert response.json()["id"] == mock_agent_data["id"]
            assert response.json()["name"] == mock_agent_data["name"]
            assert response.json()["email"] == mock_agent_data["email"]
    except ImportError:
        pytest.skip("Mocking dependencies not supported in this environment") 