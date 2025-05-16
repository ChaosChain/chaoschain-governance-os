"""
Integration tests for the ChaosCore API Gateway Studios endpoints.

This module provides tests for the Studios endpoints.
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
from chaoscore.core.studio import StudioManager


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
        
        # Mock studio
        class MockStudio:
            def get_id(self):
                return "studio-123"
            
            def get_name(self):
                return "Test Studio"
            
            def get_description(self):
                return "Test studio description"
            
            def get_created_at(self):
                return "2023-01-01T00:00:00Z"
            
            def get_owner_id(self):
                return mock_agent_data["id"]
            
            def get_members(self):
                return [
                    {
                        "agent_id": "agent-456",
                        "role": "member",
                        "permissions": ["read", "write"]
                    }
                ]
            
            def get_settings(self):
                return {"setting1": "value1"}
        
        # Mock the studio manager
        with patch.object(StudioManager, 'create_studio') as mock_create_studio:
            mock_create_studio.return_value = "studio-123"
            
            with patch.object(StudioManager, 'get_studio') as mock_get_studio:
                mock_get_studio.return_value = MockStudio()
                
                with patch.object(StudioManager, 'list_studios') as mock_list_studios:
                    mock_list_studios.return_value = [MockStudio()]
                    
                    with patch.object(StudioManager, 'add_studio_member') as mock_add_member:
                        mock_add_member.return_value = True
                        
                        with patch.object(StudioManager, 'remove_studio_member') as mock_remove_member:
                            mock_remove_member.return_value = True
                            
                            yield {
                                "mock_get_agent": mock_get_agent,
                                "mock_create_studio": mock_create_studio,
                                "mock_get_studio": mock_get_studio,
                                "mock_list_studios": mock_list_studios,
                                "mock_add_member": mock_add_member,
                                "mock_remove_member": mock_remove_member
                            }


def test_create_studio(client, mock_token, setup_mocks):
    """Test creating a studio."""
    studio_data = {
        "name": "Test Studio",
        "description": "Test studio description",
        "members": [
            {
                "agent_id": "agent-456",
                "role": "member",
                "permissions": ["read", "write"]
            }
        ],
        "settings": {
            "setting1": "value1"
        }
    }
    
    response = client.post(
        "/studios",
        json=studio_data,
        headers={"Authorization": f"Bearer {mock_token}"}
    )
    
    assert response.status_code == 201
    assert response.json()["name"] == studio_data["name"]
    assert response.json()["description"] == studio_data["description"]
    assert setup_mocks["mock_create_studio"].called


def test_list_studios(client, mock_token, setup_mocks):
    """Test listing studios."""
    response = client.get(
        "/studios",
        headers={"Authorization": f"Bearer {mock_token}"}
    )
    
    assert response.status_code == 200
    assert "studios" in response.json()
    assert "total" in response.json()
    assert "page" in response.json()
    assert "page_size" in response.json()
    assert setup_mocks["mock_list_studios"].called


def test_get_studio(client, mock_token, setup_mocks):
    """Test getting a studio."""
    response = client.get(
        "/studios/studio-123",
        headers={"Authorization": f"Bearer {mock_token}"}
    )
    
    assert response.status_code == 200
    assert response.json()["id"] == "studio-123"
    assert response.json()["name"] == "Test Studio"
    assert setup_mocks["mock_get_studio"].called


def test_add_member(client, mock_token, setup_mocks):
    """Test adding a member to a studio."""
    member_data = {
        "agent_id": "agent-789",
        "role": "developer",
        "permissions": ["read", "write", "deploy"]
    }
    
    response = client.post(
        "/studios/studio-123/members",
        json=member_data,
        headers={"Authorization": f"Bearer {mock_token}"}
    )
    
    assert response.status_code == 200
    assert setup_mocks["mock_add_member"].called


def test_remove_member(client, mock_token, setup_mocks):
    """Test removing a member from a studio."""
    response = client.delete(
        "/studios/studio-123/members/agent-456",
        headers={"Authorization": f"Bearer {mock_token}"}
    )
    
    assert response.status_code == 200
    assert setup_mocks["mock_remove_member"].called 