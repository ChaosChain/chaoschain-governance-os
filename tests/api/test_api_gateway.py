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
        "private_key": """
-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEAvnysRmP1qGA7Vdjbrt7iLr3Pw+cH1CV+qVe2ax4sZeV87yWj
JqeKBXvnqxL37IKE1QQq9rZ8DCn9DGKR2OhK+Q+qlpZa7Shf3r6IKZFcFKJqHiAe
qxH+mpLDNoLXz+4TDY9OK8jG5XQBRl4GpRQAIAJSP8vUP1FiQbWYxFYqFPkP0f/V
iOZWkpJfDVgqCDBs38Qj0S8lfgcZI2T8qRCOyECILsXqLwXHVJ7vJQH1yKb/SJyX
nU8uswO4FzyA9sMCVokLbTTrqfBPeKBKs5yX7LYCxzk/+seKXLtBGdmQpPJQvGkW
wQPSoLQlKMgQaXyYbGR7VpH6TIk8zB+rb/LyQQIDAQABAoIBAGoZQcejRm0S6L0n
3QNxPsLdUz3RPiU7RBcmZeHOcB3vN/qLplvvl3+wWAPWxrfPxQipya52d9EEXr1M
cPwRMPr/f5RJWbSBCJTLvbfRONIUjUj6IyTJALhFuXHxwNlmCY3WXTNa1+p7TRZW
Rc9uBfkJFvsi+kG/7PmS3IJkhVxnNLVyGBBDDGqUP4Svq9CCoR2YzdmG6qfeK2GQ
+AjnF/WDrS+ywknQim8IiHG7W9QreKuQd5+4louLTFCW7AdJvbxNQTQUFQK4TJbM
FkDT3WbqxRc428CzQZc+5mYcTkU70f5HjcOrVLWdhW9LzXxeJ12QPKUJd76+h0xq
PG4BpgECgYEA9sMnBZHwp6za5sNtjl3kiV6ZwFEXW7J08PgioiAXSRUDkO+t1hkj
nWh57xKqvnL9BKU1jsJyG8r/F/iJf5jQrDh7nCM5xqQsA9hGiK89U5/+4/ZUYeAC
SYWjDTMpIABP6CRdnIl3Z+TPqzMVbFr9LI9T/2arMXsRtypzWYDhLuECgYEAxXBq
CJjm3hsJf9tZJH9mHPdkHzq4ACzCNwmRVDCmI9BptM/jqQQOUbOD9Gnp9MUjG0pi
J0zWiL8FOk/PaEZ/6nM9yzLXIOsu7KWmDJsD8Gv5ZGedKuFzM1jTJYQ6rCSnYJBq
xtkJvba8fKf4x3q4+YgKLZOHwb44Qm7U2kKdXKECgYBSZj23vRKYgXwMqJQTjXLz
CnrWDvHoHb+FUxdkfYFQn7hKDkF2NxvQD6/UVxFYiQcBt3ZnXLUy/K+JIgsrHKdk
KuK0BZr7HLZTZvwNtOUWnwEp6eMSVaiYlP8TMY9kkRah9vF084wAm3bQ0+hcHXzL
wlgZKVhjvHJKB+qcqVW+wQKBgQC0guo9eZi/MytCgCJYhUUAQqRZkJ0ww/rKm3LD
GXUL/6d3qc4Kx4AaMJ0l/P6/6AkbWu9lL5qVSzH4um5QTLwPnRJnkPchrE/+dXV6
qA8hXI16HKwAlIkxP7QCqc1uQ8fIpegl6h4YGUQSlhGABRRbwYImE9E8ZKEH4GSt
zNqFIQKBgGzwGZvm6dviQrwBlLzQYPJ+WbfEjHmW7Q2RVMO2cE5jPUCuZtBSTAZp
PwJlKTQnBgKrKEZE8CbKPdKQFVrNFsv8a0tHZ9RHmfJxAqRFgSKQCuGELLgxm3mO
GQifG4l5oPJvVQsiGG3DdVz7CzNN7kkXUgFYkCqE/W+BKTdCnCA0
-----END RSA PRIVATE KEY-----
        """,
        "public_key": """
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAvnysRmP1qGA7Vdjbrt7i
Lr3Pw+cH1CV+qVe2ax4sZeV87yWjJqeKBXvnqxL37IKE1QQq9rZ8DCn9DGKR2OhK
+Q+qlpZa7Shf3r6IKZFcFKJqHiAeqxH+mpLDNoLXz+4TDY9OK8jG5XQBRl4GpRQA
IAJSP8vUP1FiQbWYxFYqFPkP0f/ViOZWkpJfDVgqCDBs38Qj0S8lfgcZI2T8qRCO
yECILsXqLwXHVJ7vJQH1yKb/SJyXnU8uswO4FzyA9sMCVokLbTTrqfBPeKBKs5yX
7LYCxzk/+seKXLtBGdmQpPJQvGkWwQPSoLQlKMgQaXyYbGR7VpH6TIk8zB+rb/Ly
QQIDAQAB
-----END PUBLIC KEY-----
        """
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