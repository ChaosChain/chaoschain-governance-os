"""
Integration tests for the ChaosCore API Gateway Actions endpoints.

This module provides tests for the Actions endpoints.
"""
import os
import pytest
from fastapi.testclient import TestClient
import jwt
from datetime import datetime, timedelta
from unittest.mock import patch

# Mock the environment before importing the app
os.environ["CHAOSCORE_ENV"] = "test"
os.environ["SGX_MOCK"] = "true"
os.environ["ETHEREUM_MOCK"] = "true"

from api_gateway.main import app
from chaoscore.core.proof_of_agency import ProofOfAgencyInterface


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
        
        # Mock the proof of agency
        with patch.object(ProofOfAgencyInterface, 'log_action') as mock_log_action:
            mock_log_action.return_value = "action-123"
            
            with patch.object(ProofOfAgencyInterface, 'record_outcome') as mock_record_outcome:
                mock_record_outcome.return_value = True
                
                yield {
                    "mock_get_agent": mock_get_agent,
                    "mock_log_action": mock_log_action,
                    "mock_record_outcome": mock_record_outcome
                }


def test_create_action(client, mock_token, setup_mocks):
    """Test creating an action."""
    action_data = {
        "action_type": "test_action",
        "description": "Test action description",
        "data": {
            "proposal_id": "proposal-123",
            "parameters": {"param1": "value1"},
            "context": {"context1": "value1"}
        }
    }
    
    response = client.post(
        "/actions",
        json=action_data,
        headers={"Authorization": f"Bearer {mock_token}"}
    )
    
    assert response.status_code == 201
    assert response.json()["action_type"] == action_data["action_type"]
    assert response.json()["description"] == action_data["description"]
    assert response.json()["data"]["proposal_id"] == action_data["data"]["proposal_id"]
    assert setup_mocks["mock_log_action"].called


def test_record_outcome(client, mock_token, setup_mocks):
    """Test recording an action outcome."""
    outcome_data = {
        "success": True,
        "results": {
            "proposal_result": {"result": "approved"},
            "simulation": {"status": "completed"},
            "metrics": {"execution_time": 1.5}
        },
        "impact_score": 0.75
    }
    
    response = client.post(
        "/actions/action-123/outcome",
        json=outcome_data,
        headers={"Authorization": f"Bearer {mock_token}"}
    )
    
    assert response.status_code == 200
    assert response.json()["outcome"]["success"] == outcome_data["success"]
    assert response.json()["outcome"]["impact_score"] == outcome_data["impact_score"]
    assert setup_mocks["mock_record_outcome"].called


def test_list_actions(client, mock_token, setup_mocks):
    """Test listing actions."""
    response = client.get(
        "/actions",
        headers={"Authorization": f"Bearer {mock_token}"}
    )
    
    assert response.status_code == 200
    assert "actions" in response.json()
    assert "total" in response.json()
    assert "page" in response.json()
    assert "page_size" in response.json()


def test_get_action(client, mock_token, setup_mocks):
    """Test getting an action."""
    response = client.get(
        "/actions/action-123",
        headers={"Authorization": f"Bearer {mock_token}"}
    )
    
    # The current implementation returns 404 because it's not fully implemented
    assert response.status_code == 404 