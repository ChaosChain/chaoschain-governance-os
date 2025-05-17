"""
ChaosCore Client

This module provides the main client for interacting with the ChaosCore API Gateway.
"""

import json
import logging
import requests
from typing import Dict, List, Optional, Any, Union
from urllib.parse import urljoin

from sdk.chaoscore.exceptions import (
    ChaosCoreAPIError,
    ChaosCoreAuthError,
    ChaosCoreConnectionError,
    ChaosCoreNotFoundError,
)

logger = logging.getLogger(__name__)

class ChaosCore:
    """
    ChaosCore API client.
    
    This client provides methods for interacting with the ChaosCore API Gateway.
    """
    
    def __init__(
        self, 
        base_url: str = "http://localhost:8000",
        token: Optional[str] = None,
        timeout: int = 30
    ):
        """
        Initialize a new ChaosCore client.
        
        Args:
            base_url: The base URL of the ChaosCore API Gateway
            token: JWT token for authentication (optional)
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/") + "/"
        self.token = token
        self.timeout = timeout
        self.session = requests.Session()
        
        # Configure headers for all requests
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": f"ChaosCore-SDK/0.1.0"
        })
        
        if token:
            self.session.headers.update({
                "Authorization": f"Bearer {token}"
            })
        
        logger.debug(f"Initialized ChaosCore client with base URL: {self.base_url}")
    
    def _request(
        self, 
        method: str, 
        endpoint: str, 
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> Dict:
        """
        Make a request to the ChaosCore API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint
            params: Query parameters
            data: Request data
            headers: Custom headers
            
        Returns:
            Response data
            
        Raises:
            ChaosCoreConnectionError: If the connection fails
            ChaosCoreAuthError: If authentication fails
            ChaosCoreNotFoundError: If the resource is not found
            ChaosCoreAPIError: If the API returns an error
        """
        url = urljoin(self.base_url, endpoint)
        request_headers = {}
        
        if headers:
            request_headers.update(headers)
        
        try:
            logger.debug(f"{method} {url}")
            
            if data:
                if isinstance(data, dict):
                    data = json.dumps(data)
                logger.debug(f"Request data: {data}")
            
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                data=data,
                headers=request_headers,
                timeout=self.timeout
            )
            
            # Log response details
            logger.debug(f"Response status: {response.status_code}")
            
            # Handle different status codes
            if response.status_code == 204:
                return {}
            
            if response.status_code == 404:
                raise ChaosCoreNotFoundError(f"Resource not found: {endpoint}")
            
            if response.status_code == 401:
                raise ChaosCoreAuthError("Authentication failed")
            
            if response.status_code == 403:
                raise ChaosCoreAuthError("Permission denied")
            
            if response.status_code >= 400:
                error_data = {}
                try:
                    error_data = response.json()
                except:
                    error_data = {"detail": response.text}
                
                raise ChaosCoreAPIError(
                    f"API error ({response.status_code}): {error_data.get('detail', 'Unknown error')}"
                )
            
            # Parse JSON response
            try:
                if response.text:
                    return response.json()
                return {}
            except json.JSONDecodeError:
                logger.error(f"Failed to parse JSON response: {response.text}")
                raise ChaosCoreAPIError("Invalid JSON response from the API")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Connection error: {e}")
            raise ChaosCoreConnectionError(f"Failed to connect to the API: {e}")
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        Make a GET request to the ChaosCore API.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            
        Returns:
            Response data
        """
        return self._request("GET", endpoint, params=params)
    
    def post(self, endpoint: str, data: Dict, params: Optional[Dict] = None) -> Dict:
        """
        Make a POST request to the ChaosCore API.
        
        Args:
            endpoint: API endpoint
            data: Request data
            params: Query parameters
            
        Returns:
            Response data
        """
        return self._request("POST", endpoint, params=params, data=data)
    
    def put(self, endpoint: str, data: Dict, params: Optional[Dict] = None) -> Dict:
        """
        Make a PUT request to the ChaosCore API.
        
        Args:
            endpoint: API endpoint
            data: Request data
            params: Query parameters
            
        Returns:
            Response data
        """
        return self._request("PUT", endpoint, params=params, data=data)
    
    def delete(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        Make a DELETE request to the ChaosCore API.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            
        Returns:
            Response data
        """
        return self._request("DELETE", endpoint, params=params)
    
    def register_agent(self, name: str, email: str, metadata: Optional[Dict] = None) -> Dict:
        """
        Register a new agent.
        
        Args:
            name: Agent name
            email: Agent email
            metadata: Additional metadata
            
        Returns:
            Agent registration response
        """
        data = {
            "name": name,
            "email": email,
            "metadata": metadata or {}
        }
        
        response = self.post("agents", data)
        
        # Update client token with the new agent token
        if "token" in response:
            self.token = response["token"]
            self.session.headers.update({
                "Authorization": f"Bearer {self.token}"
            })
        
        return response
    
    def get_agent(self, agent_id: str) -> Dict:
        """
        Get agent details.
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Agent details
        """
        return self.get(f"agents/{agent_id}")
    
    def list_agents(self, limit: int = 100, offset: int = 0) -> Dict:
        """
        List agents.
        
        Args:
            limit: Maximum number of agents to return
            offset: Number of agents to skip
            
        Returns:
            List of agents
        """
        return self.get("agents", params={"limit": limit, "offset": offset})
    
    def log_action(self, action_type: str, description: str, data: Dict) -> Dict:
        """
        Log an action.
        
        Args:
            action_type: Type of action
            description: Action description
            data: Action data
            
        Returns:
            Logged action details
        """
        action_data = {
            "action_type": action_type,
            "description": description,
            "data": data
        }
        
        return self.post("actions", action_data)
    
    def record_outcome(self, action_id: str, success: bool, results: Dict, impact_score: float = 0.0) -> Dict:
        """
        Record an outcome for an action.
        
        Args:
            action_id: Action ID
            success: Whether the action was successful
            results: Results of the action
            impact_score: Impact score (0.0-1.0)
            
        Returns:
            Recorded outcome details
        """
        outcome_data = {
            "success": success,
            "results": results,
            "impact_score": impact_score
        }
        
        return self.post(f"actions/{action_id}/outcomes", outcome_data)
    
    def get_action(self, action_id: str) -> Dict:
        """
        Get action details.
        
        Args:
            action_id: Action ID
            
        Returns:
            Action details
        """
        return self.get(f"actions/{action_id}")
    
    def list_actions(self, limit: int = 100, offset: int = 0, 
                     action_type: Optional[str] = None, agent_id: Optional[str] = None) -> Dict:
        """
        List actions.
        
        Args:
            limit: Maximum number of actions to return
            offset: Number of actions to skip
            action_type: Filter by action type
            agent_id: Filter by agent ID
            
        Returns:
            List of actions
        """
        params = {"limit": limit, "offset": offset}
        
        if action_type:
            params["action_type"] = action_type
        
        if agent_id:
            params["agent_id"] = agent_id
        
        return self.get("actions", params=params)
    
    def create_studio(self, name: str, description: str, metadata: Optional[Dict] = None) -> Dict:
        """
        Create a new studio.
        
        Args:
            name: Studio name
            description: Studio description
            metadata: Additional metadata
            
        Returns:
            Created studio details
        """
        studio_data = {
            "name": name,
            "description": description,
            "metadata": metadata or {}
        }
        
        return self.post("studios", studio_data)
    
    def get_studio(self, studio_id: str) -> Dict:
        """
        Get studio details.
        
        Args:
            studio_id: Studio ID
            
        Returns:
            Studio details
        """
        return self.get(f"studios/{studio_id}")
    
    def list_studios(self, limit: int = 100, offset: int = 0) -> Dict:
        """
        List studios.
        
        Args:
            limit: Maximum number of studios to return
            offset: Number of studios to skip
            
        Returns:
            List of studios
        """
        return self.get("studios", params={"limit": limit, "offset": offset})
    
    def create_task(self, studio_id: str, name: str, description: str, parameters: Optional[Dict] = None) -> Dict:
        """
        Create a new task in a studio.
        
        Args:
            studio_id: Studio ID
            name: Task name
            description: Task description
            parameters: Task parameters
            
        Returns:
            Created task details
        """
        task_data = {
            "name": name,
            "description": description,
            "parameters": parameters or {}
        }
        
        return self.post(f"studios/{studio_id}/tasks", task_data)
    
    def get_task(self, studio_id: str, task_id: str) -> Dict:
        """
        Get task details.
        
        Args:
            studio_id: Studio ID
            task_id: Task ID
            
        Returns:
            Task details
        """
        return self.get(f"studios/{studio_id}/tasks/{task_id}")
    
    def list_tasks(self, studio_id: str, limit: int = 100, offset: int = 0) -> Dict:
        """
        List tasks in a studio.
        
        Args:
            studio_id: Studio ID
            limit: Maximum number of tasks to return
            offset: Number of tasks to skip
            
        Returns:
            List of tasks
        """
        return self.get(f"studios/{studio_id}/tasks", params={"limit": limit, "offset": offset})
    
    def get_agent_reputation(self, agent_id: str) -> Dict:
        """
        Get agent reputation.
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Agent reputation
        """
        return self.get(f"reputation/agents/{agent_id}")
    
    def rotate_jwt_key(self) -> Dict:
        """
        Rotate the JWT signing key.
        
        This requires authentication and should only be called by admin agents.
        
        Returns:
            Key rotation response
        """
        return self.post("auth/rotate-key", {})
    
    def get_auth_status(self) -> Dict:
        """
        Get authentication system status.
        
        This requires authentication and should only be called by admin agents.
        
        Returns:
            Authentication system status
        """
        return self.get("auth/status")
    
    def check_health(self) -> Dict:
        """
        Check API health.
        
        Returns:
            Health check response
        """
        return self.get("health") 