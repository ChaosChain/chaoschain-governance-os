"""
Integration tests for the ChaosCore API Gateway Reputation endpoints.

This module provides tests for the Reputation endpoints.
"""
import os
import pytest
from fastapi.testclient import TestClient
import jwt
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Mock the environment before importing the app
os.environ["CHAOSCORE_ENV"] = "test"
os.environ["SGX_MOCK"] = "true"
os.environ["ETHEREUM_MOCK"] = "true"

from api_gateway.main import app
from chaoscore.core.reputation import ReputationSystem


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


@pytest.fixture
def setup_mocks(mock_agent_data):
    """Set up mocks for testing."""
    # Mock the agent registry to return our mock agent
    from chaoscore.core.agent_registry import AgentRegistryInterface
    
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
        
        # Mock the reputation system
        with patch.object(ReputationSystem, 'get_reputation') as mock_get_reputation:
            mock_get_reputation.return_value = 0.85
            
            with patch.object(ReputationSystem, 'get_last_update') as mock_get_last_update:
                mock_get_last_update.return_value = "2023-01-01T00:00:00Z"
                
                with patch.object(ReputationSystem, 'get_history') as mock_get_history:
                    mock_get_history.return_value = [
                        {
                            "score": 0.85,
                            "category": "governance",
                            "timestamp": "2023-01-01T00:00:00Z",
                            "reason": "Good proposal",
                            "action_id": "action-123"
                        }
                    ]
                    
                    with patch.object(ReputationSystem, 'update_reputation') as mock_update_reputation:
                        mock_update_reputation.return_value = True
                        
                        with patch.object(ReputationSystem, 'get_top_agents') as mock_get_top_agents:
                            mock_get_top_agents.return_value = [
                                {
                                    "agent_id": mock_agent_data["id"],
                                    "score": 0.85,
                                    "updated_at": "2023-01-01T00:00:00Z"
                                }
                            ]
                            
                            yield {
                                "mock_get_agent": mock_get_agent,
                                "mock_get_reputation": mock_get_reputation,
                                "mock_get_last_update": mock_get_last_update,
                                "mock_get_history": mock_get_history,
                                "mock_update_reputation": mock_update_reputation,
                                "mock_get_top_agents": mock_get_top_agents
                            }


def test_get_reputation(client, mock_token, setup_mocks):
    """Test getting an agent's reputation."""
    response = client.get(
        "/reputation/agents/agent-123",
        headers={"Authorization": f"Bearer {mock_token}"}
    )
    
    assert response.status_code == 200
    assert response.json()["agent_id"] == "agent-123"
    assert response.json()["score"] == 0.85
    assert setup_mocks["mock_get_reputation"].called


def test_get_reputation_history(client, mock_token, setup_mocks):
    """Test getting an agent's reputation history."""
    response = client.get(
        "/reputation/agents/agent-123/history",
        headers={"Authorization": f"Bearer {mock_token}"}
    )
    
    assert response.status_code == 200
    assert "history" in response.json()
    assert "total" in response.json()
    assert "page" in response.json()
    assert "page_size" in response.json()
    assert setup_mocks["mock_get_history"].called


def test_update_reputation(client, mock_token, setup_mocks):
    """Test updating an agent's reputation."""
    update_data = {
        "score_delta": 0.1,
        "category": "governance",
        "reason": "Great proposal implementation",
        "action_id": "action-456"
    }
    
    response = client.post(
        "/reputation/agents/agent-456",
        json=update_data,
        headers={"Authorization": f"Bearer {mock_token}"}
    )
    
    assert response.status_code == 200
    assert response.json()["agent_id"] == "agent-456"
    assert response.json()["category"] == "governance"
    assert setup_mocks["mock_update_reputation"].called


def test_get_top_agents(client, mock_token, setup_mocks):
    """Test getting top agents by reputation."""
    response = client.get(
        "/reputation/top",
        headers={"Authorization": f"Bearer {mock_token}"}
    )
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0
    assert setup_mocks["mock_get_top_agents"].called 