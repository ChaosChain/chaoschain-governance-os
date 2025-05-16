"""
API Gateway Integration Test

This module provides integration tests for the ChaosCore API Gateway.
"""

import os
import pytest
import requests
from typing import Dict, Any

# Set test mode environment variable
os.environ["SQLITE_TEST_MODE"] = "true"

# Import the FastAPI app
from api_gateway.main import app
from fastapi.testclient import TestClient

# Create a test client
client = TestClient(app)

# --- Test Data ---

test_agent = {
    "name": "Test Agent",
    "email": "test@example.com",
    "metadata": {
        "role": "Tester",
        "expertise": "API Testing",
        "version": "1.0.0"
    }
}

test_action = {
    "action_type": "TEST",
    "description": "Testing the API Gateway",
    "data": {
        "test_id": "integration_test_001",
        "components": ["agents", "actions", "studios", "reputation"]
    }
}

test_outcome = {
    "success": True,
    "results": {
        "tests_passed": 10,
        "tests_failed": 0,
        "coverage": "95%"
    },
    "impact_score": 0.9
}

test_studio = {
    "name": "Test Studio",
    "description": "Studio for API testing",
    "metadata": {
        "domain": "testing",
        "version": "1.0.0",
        "tags": ["test", "integration", "api"]
    }
}

test_task = {
    "name": "Run API Tests",
    "description": "Execute integration tests for the API Gateway",
    "parameters": {
        "priority": "high",
        "timeout": 60,
        "retry_count": 3
    }
}

# --- Test Functions ---

class TestAPIGateway:
    """Test cases for the API Gateway."""
    
    def setup_method(self):
        """Set up test data before each test."""
        self.agent_id = None
        self.token = None
        self.action_id = None
        self.studio_id = None
    
    def test_01_root_endpoint(self):
        """Test the root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "ChaosCore API Gateway"
        assert data["status"] == "operational"
    
    def test_02_health_check(self):
        """Test the health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_03_register_agent(self):
        """Test registering an agent."""
        response = client.post("/agents", json=test_agent)
        assert response.status_code == 201
        data = response.json()
        assert "agent_id" in data
        assert "token" in data
        
        # Store for later tests
        self.agent_id = data["agent_id"]
        self.token = data["token"]
    
    def test_04_get_agent(self):
        """Test getting an agent."""
        assert self.agent_id is not None
        assert self.token is not None
        
        headers = {"Authorization": f"Bearer {self.token}"}
        response = client.get(f"/agents/{self.agent_id}", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == self.agent_id
        assert data["name"] == test_agent["name"]
        assert data["email"] == test_agent["email"]
    
    def test_05_list_agents(self):
        """Test listing agents."""
        assert self.token is not None
        
        headers = {"Authorization": f"Bearer {self.token}"}
        response = client.get("/agents", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "agents" in data
        assert isinstance(data["agents"], list)
        assert len(data["agents"]) > 0
    
    def test_06_log_action(self):
        """Test logging an action."""
        assert self.token is not None
        
        headers = {"Authorization": f"Bearer {self.token}"}
        response = client.post("/actions", json=test_action, headers=headers)
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["agent_id"] == self.agent_id
        assert data["action_type"] == test_action["action_type"]
        
        # Store for later tests
        self.action_id = data["id"]
    
    def test_07_record_outcome(self):
        """Test recording an outcome."""
        assert self.token is not None
        assert self.action_id is not None
        
        headers = {"Authorization": f"Bearer {self.token}"}
        response = client.post(f"/actions/{self.action_id}/outcomes", json=test_outcome, headers=headers)
        assert response.status_code == 201
        data = response.json()
        assert data["action_id"] == self.action_id
        assert data["success"] == test_outcome["success"]
        assert data["impact_score"] == test_outcome["impact_score"]
    
    def test_08_create_studio(self):
        """Test creating a studio."""
        assert self.token is not None
        
        headers = {"Authorization": f"Bearer {self.token}"}
        response = client.post("/studios", json=test_studio, headers=headers)
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["name"] == test_studio["name"]
        assert data["description"] == test_studio["description"]
        assert data["owner_id"] == self.agent_id
        
        # Store for later tests
        self.studio_id = data["id"]
    
    def test_09_get_studio(self):
        """Test getting a studio."""
        assert self.token is not None
        assert self.studio_id is not None
        
        headers = {"Authorization": f"Bearer {self.token}"}
        response = client.get(f"/studios/{self.studio_id}", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == self.studio_id
        assert data["name"] == test_studio["name"]
        assert data["description"] == test_studio["description"]
    
    def test_10_list_studios(self):
        """Test listing studios."""
        assert self.token is not None
        
        headers = {"Authorization": f"Bearer {self.token}"}
        response = client.get("/studios", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "studios" in data
        assert isinstance(data["studios"], list)
        assert len(data["studios"]) > 0
    
    def test_11_create_task(self):
        """Test creating a task."""
        assert self.token is not None
        assert self.studio_id is not None
        
        headers = {"Authorization": f"Bearer {self.token}"}
        response = client.post(f"/studios/{self.studio_id}/tasks", json=test_task, headers=headers)
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["studio_id"] == self.studio_id
        assert data["name"] == test_task["name"]
        assert data["description"] == test_task["description"]
    
    def test_12_get_agent_reputation(self):
        """Test getting agent reputation."""
        assert self.token is not None
        assert self.agent_id is not None
        
        headers = {"Authorization": f"Bearer {self.token}"}
        response = client.get(f"/reputation/agents/{self.agent_id}", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["agent_id"] == self.agent_id
        assert "score" in data
        assert "components" in data
    
    def test_13_list_agent_reputations(self):
        """Test listing agent reputations."""
        assert self.token is not None
        
        headers = {"Authorization": f"Bearer {self.token}"}
        response = client.get("/reputation/agents", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "reputations" in data
        assert isinstance(data["reputations"], list)
    
    def test_14_get_domain_reputation_leaderboard(self):
        """Test getting domain reputation leaderboard."""
        assert self.token is not None
        
        headers = {"Authorization": f"Bearer {self.token}"}
        response = client.get("/reputation/domains/testing", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "reputations" in data
        assert isinstance(data["reputations"], list)


# Run the tests
if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 