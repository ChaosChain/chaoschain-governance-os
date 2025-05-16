"""
ChaosCore API Gateway Client Example

This module provides a simple example of how to use the ChaosCore API Gateway.
"""

import requests
import json
from typing import Dict, Any, Optional, List

class ChaosCorePlatformClient:
    """
    Client for interacting with the ChaosCore Platform API Gateway.
    """
    
    def __init__(self, base_url: str = "http://localhost:8000", token: Optional[str] = None):
        """
        Initialize the ChaosCore Platform client.
        
        Args:
            base_url: Base URL of the API Gateway
            token: Optional JWT token for authentication
        """
        self.base_url = base_url
        self.token = token
        self.headers = {}
        
        if token:
            self.headers["Authorization"] = f"Bearer {token}"
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make an HTTP request to the API Gateway.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            data: Request data
            
        Returns:
            Response data
        """
        url = f"{self.base_url}{endpoint}"
        
        if method == "GET":
            response = requests.get(url, headers=self.headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=self.headers)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        # Check for successful response
        response.raise_for_status()
        
        return response.json()
    
    # --- Agent Methods ---
    
    def register_agent(self, name: str, email: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Register a new agent.
        
        Args:
            name: Agent name
            email: Agent email
            metadata: Optional agent metadata
            
        Returns:
            Registration response with agent ID and token
        """
        data = {
            "name": name,
            "email": email
        }
        
        if metadata:
            data["metadata"] = metadata
        
        response = self._make_request("POST", "/agents", data)
        
        # Store the token for future requests
        self.token = response["token"]
        self.headers["Authorization"] = f"Bearer {self.token}"
        
        return response
    
    def get_agent(self, agent_id: str) -> Dict[str, Any]:
        """
        Get agent by ID.
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Agent data
        """
        return self._make_request("GET", f"/agents/{agent_id}")
    
    def list_agents(self, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        """
        List agents with pagination.
        
        Args:
            limit: Maximum number of agents to return
            offset: Offset for pagination
            
        Returns:
            List of agents
        """
        return self._make_request("GET", f"/agents?limit={limit}&offset={offset}")
    
    # --- Action Methods ---
    
    def log_action(self, action_type: str, description: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Log an action.
        
        Args:
            action_type: Type of action
            description: Description of the action
            data: Optional action data
            
        Returns:
            Action data
        """
        request_data = {
            "action_type": action_type,
            "description": description
        }
        
        if data:
            request_data["data"] = data
        
        return self._make_request("POST", "/actions", request_data)
    
    def record_outcome(self, action_id: str, success: bool, results: Optional[Dict[str, Any]] = None,
                     impact_score: float = 0.0) -> Dict[str, Any]:
        """
        Record the outcome of an action.
        
        Args:
            action_id: Action ID
            success: Whether the action was successful
            results: Optional action results
            impact_score: Impact score of the action
            
        Returns:
            Outcome data
        """
        data = {
            "success": success,
            "impact_score": impact_score
        }
        
        if results:
            data["results"] = results
        
        return self._make_request("POST", f"/actions/{action_id}/outcomes", data)
    
    # --- Studio Methods ---
    
    def create_studio(self, name: str, description: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a new studio.
        
        Args:
            name: Studio name
            description: Studio description
            metadata: Optional studio metadata
            
        Returns:
            Studio data
        """
        data = {
            "name": name,
            "description": description
        }
        
        if metadata:
            data["metadata"] = metadata
        
        return self._make_request("POST", "/studios", data)
    
    def get_studio(self, studio_id: str) -> Dict[str, Any]:
        """
        Get studio by ID.
        
        Args:
            studio_id: Studio ID
            
        Returns:
            Studio data
        """
        return self._make_request("GET", f"/studios/{studio_id}")
    
    def list_studios(self, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        """
        List studios with pagination.
        
        Args:
            limit: Maximum number of studios to return
            offset: Offset for pagination
            
        Returns:
            List of studios
        """
        return self._make_request("GET", f"/studios?limit={limit}&offset={offset}")
    
    def create_task(self, studio_id: str, name: str, description: str, 
                  parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a new task in a studio.
        
        Args:
            studio_id: Studio ID
            name: Task name
            description: Task description
            parameters: Optional task parameters
            
        Returns:
            Task data
        """
        data = {
            "name": name,
            "description": description
        }
        
        if parameters:
            data["parameters"] = parameters
        
        return self._make_request("POST", f"/studios/{studio_id}/tasks", data)
    
    # --- Reputation Methods ---
    
    def get_agent_reputation(self, agent_id: str) -> Dict[str, Any]:
        """
        Get reputation for an agent.
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Agent reputation data
        """
        return self._make_request("GET", f"/reputation/agents/{agent_id}")
    
    def list_agent_reputations(self, limit: int = 10, offset: int = 0, 
                             min_score: Optional[float] = None, 
                             domain: Optional[str] = None) -> Dict[str, Any]:
        """
        List agent reputations with pagination and filtering.
        
        Args:
            limit: Maximum number of reputations to return
            offset: Offset for pagination
            min_score: Minimum reputation score filter
            domain: Reputation domain filter
            
        Returns:
            List of agent reputations
        """
        params = f"limit={limit}&offset={offset}"
        
        if min_score is not None:
            params += f"&min_score={min_score}"
        
        if domain:
            params += f"&domain={domain}"
        
        return self._make_request("GET", f"/reputation/agents?{params}")
    
    def get_domain_reputation_leaderboard(self, domain: str, limit: int = 10, 
                                        offset: int = 0) -> Dict[str, Any]:
        """
        Get reputation leaderboard for a specific domain.
        
        Args:
            domain: Reputation domain
            limit: Maximum number of agents to return
            offset: Offset for pagination
            
        Returns:
            List of agent reputations for the domain
        """
        return self._make_request("GET", f"/reputation/domains/{domain}?limit={limit}&offset={offset}")


# Example usage of the client
if __name__ == "__main__":
    # Create the client
    client = ChaosCorePlatformClient()
    
    # Register an agent
    print("Registering an agent...")
    agent = client.register_agent(
        name="Example Agent",
        email="agent@example.com",
        metadata={
            "role": "Researcher",
            "expertise": "Blockchain Governance",
            "version": "1.0.0"
        }
    )
    
    agent_id = agent["agent_id"]
    print(f"Agent registered with ID: {agent_id}")
    
    # Log some actions
    print("\nLogging actions...")
    action = client.log_action(
        action_type="RESEARCH",
        description="Researching blockchain governance mechanisms",
        data={
            "sources": ["academic_papers", "chain_data"],
            "metrics": ["gas_usage", "proposal_success_rate"]
        }
    )
    
    action_id = action["id"]
    print(f"Action logged with ID: {action_id}")
    
    # Record the outcome
    print("\nRecording outcome...")
    outcome = client.record_outcome(
        action_id=action_id,
        success=True,
        results={
            "findings": "Discovered correlation between gas optimization and proposal success",
            "recommendations": ["Implement gas estimation", "Optimize contract calls"]
        },
        impact_score=0.8
    )
    
    print(f"Outcome recorded with success: {outcome['success']}")
    
    # Create a studio
    print("\nCreating a studio...")
    studio = client.create_studio(
        name="Governance Research Studio",
        description="Studio for researching blockchain governance mechanisms",
        metadata={
            "domain": "blockchain_governance",
            "version": "1.0.0",
            "tags": ["governance", "research", "optimization"]
        }
    )
    
    studio_id = studio["id"]
    print(f"Studio created with ID: {studio_id}")
    
    # Create a task
    print("\nCreating a task...")
    task = client.create_task(
        studio_id=studio_id,
        name="Optimize Gas Usage",
        description="Research and implement gas optimization strategies",
        parameters={
            "priority": "high",
            "deadline": "2023-12-31",
            "metrics": ["gas_reduction", "transaction_success_rate"]
        }
    )
    
    print(f"Task created with ID: {task['id']}")
    
    # Get agent reputation
    print("\nChecking agent reputation...")
    reputation = client.get_agent_reputation(agent_id)
    
    print(f"Agent reputation score: {reputation['score']}")
    
    print("\nDemo complete!") 