#!/usr/bin/env python3
"""
ChaosCore API Gateway Sample Client

This script demonstrates how to interact with the ChaosCore API Gateway
using Python. It provides examples for authentication, agent management,
action logging, and more.
"""

import argparse
import json
import os
import time
from typing import Dict, Any, List, Optional

import jwt
import requests


class ChaosGatewayClient:
    """
    ChaosCore API Gateway client.
    
    This client provides methods for interacting with the ChaosCore API Gateway.
    """
    
    def __init__(self, base_url: str):
        """
        Initialize the client.
        
        Args:
            base_url: Base URL of the API Gateway
        """
        self.base_url = base_url.rstrip('/')
        self.token = None
        self.agent_id = None
    
    def authenticate(self, agent_id: str, private_key: str) -> Dict[str, Any]:
        """
        Authenticate with the API Gateway.
        
        Args:
            agent_id: Agent ID
            private_key: Agent's private key in PEM format
            
        Returns:
            Agent information
        """
        # Create token payload
        payload = {
            "sub": agent_id,
            "exp": time.time() + 3600,  # 1 hour
            "iat": time.time()
        }
        
        # Sign token with private key
        token = jwt.encode(
            payload=payload,
            key=private_key,
            algorithm="RS256",
            headers={"kid": agent_id}
        )
        
        # Store token and agent ID
        self.token = token
        self.agent_id = agent_id
        
        # Test authentication by getting current agent
        return self.get_current_agent()
    
    def _get_headers(self) -> Dict[str, str]:
        """
        Get request headers with authentication.
        
        Returns:
            Request headers
        """
        if not self.token:
            raise ValueError("Not authenticated, call authenticate() first")
        
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def _request(self, method: str, path: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make a request to the API Gateway.
        
        Args:
            method: HTTP method
            path: API path
            data: Request data
            
        Returns:
            Response data
        """
        url = f"{self.base_url}{path}"
        headers = self._get_headers()
        
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        # Check for errors
        if response.status_code >= 400:
            raise Exception(f"API error: {response.status_code} - {response.text}")
        
        # Return response data
        return response.json() if response.text else {}
    
    # Agent methods
    def register_agent(self, name: str, email: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Register a new agent.
        
        Args:
            name: Agent name
            email: Agent email
            metadata: Agent metadata
            
        Returns:
            Created agent
        """
        data = {
            "name": name,
            "email": email,
            "metadata": metadata or {}
        }
        
        return self._request("POST", "/agents", data)
    
    def get_current_agent(self) -> Dict[str, Any]:
        """
        Get the current authenticated agent.
        
        Returns:
            Agent information
        """
        return self._request("GET", "/agents/me")
    
    def get_agent(self, agent_id: str) -> Dict[str, Any]:
        """
        Get an agent by ID.
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Agent information
        """
        return self._request("GET", f"/agents/{agent_id}")
    
    def list_agents(self, page: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """
        List agents.
        
        Args:
            page: Page number
            page_size: Page size
            
        Returns:
            List of agents
        """
        return self._request("GET", f"/agents?page={page}&page_size={page_size}")
    
    # Action methods
    def log_action(self, action_type: str, description: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Log an action.
        
        Args:
            action_type: Action type
            description: Action description
            data: Action data
            
        Returns:
            Created action
        """
        action_data = {
            "action_type": action_type,
            "description": description,
            "data": data or {}
        }
        
        return self._request("POST", "/actions", action_data)
    
    def record_outcome(self, action_id: str, success: bool, results: Optional[Dict[str, Any]] = None, impact_score: float = 0.0) -> Dict[str, Any]:
        """
        Record an action outcome.
        
        Args:
            action_id: Action ID
            success: Whether the action was successful
            results: Action results
            impact_score: Impact score
            
        Returns:
            Updated action
        """
        outcome_data = {
            "success": success,
            "results": results or {},
            "impact_score": impact_score
        }
        
        return self._request("POST", f"/actions/{action_id}/outcome", outcome_data)
    
    def list_actions(self, page: int = 1, page_size: int = 10, agent_id: Optional[str] = None, action_type: Optional[str] = None) -> Dict[str, Any]:
        """
        List actions.
        
        Args:
            page: Page number
            page_size: Page size
            agent_id: Filter by agent ID
            action_type: Filter by action type
            
        Returns:
            List of actions
        """
        query = f"?page={page}&page_size={page_size}"
        if agent_id:
            query += f"&agent_id={agent_id}"
        if action_type:
            query += f"&action_type={action_type}"
        
        return self._request("GET", f"/actions{query}")
    
    def get_action(self, action_id: str) -> Dict[str, Any]:
        """
        Get an action by ID.
        
        Args:
            action_id: Action ID
            
        Returns:
            Action information
        """
        return self._request("GET", f"/actions/{action_id}")
    
    # Studio methods
    def create_studio(self, name: str, description: str, members: Optional[List[Dict[str, Any]]] = None, settings: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a new studio.
        
        Args:
            name: Studio name
            description: Studio description
            members: Studio members
            settings: Studio settings
            
        Returns:
            Created studio
        """
        studio_data = {
            "name": name,
            "description": description,
            "members": members or [],
            "settings": settings or {}
        }
        
        return self._request("POST", "/studios", studio_data)
    
    def get_studio(self, studio_id: str) -> Dict[str, Any]:
        """
        Get a studio by ID.
        
        Args:
            studio_id: Studio ID
            
        Returns:
            Studio information
        """
        return self._request("GET", f"/studios/{studio_id}")
    
    def list_studios(self, page: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """
        List studios.
        
        Args:
            page: Page number
            page_size: Page size
            
        Returns:
            List of studios
        """
        return self._request("GET", f"/studios?page={page}&page_size={page_size}")
    
    def add_studio_member(self, studio_id: str, agent_id: str, role: str, permissions: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Add a member to a studio.
        
        Args:
            studio_id: Studio ID
            agent_id: Agent ID
            role: Member role
            permissions: Member permissions
            
        Returns:
            Updated studio
        """
        member_data = {
            "agent_id": agent_id,
            "role": role,
            "permissions": permissions or []
        }
        
        return self._request("POST", f"/studios/{studio_id}/members", member_data)
    
    def remove_studio_member(self, studio_id: str, agent_id: str) -> Dict[str, Any]:
        """
        Remove a member from a studio.
        
        Args:
            studio_id: Studio ID
            agent_id: Agent ID
            
        Returns:
            Updated studio
        """
        return self._request("DELETE", f"/studios/{studio_id}/members/{agent_id}")
    
    # Reputation methods
    def get_reputation(self, agent_id: str, category: Optional[str] = None) -> Dict[str, Any]:
        """
        Get an agent's reputation.
        
        Args:
            agent_id: Agent ID
            category: Reputation category
            
        Returns:
            Reputation information
        """
        query = f"?category={category}" if category else ""
        return self._request("GET", f"/reputation/agents/{agent_id}{query}")
    
    def get_reputation_history(self, agent_id: str, category: Optional[str] = None, page: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """
        Get an agent's reputation history.
        
        Args:
            agent_id: Agent ID
            category: Reputation category
            page: Page number
            page_size: Page size
            
        Returns:
            Reputation history
        """
        query = f"?page={page}&page_size={page_size}"
        if category:
            query += f"&category={category}"
        
        return self._request("GET", f"/reputation/agents/{agent_id}/history{query}")
    
    def update_reputation(self, agent_id: str, score_delta: float, reason: str, category: Optional[str] = None, action_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Update an agent's reputation.
        
        Args:
            agent_id: Agent ID
            score_delta: Score delta
            reason: Reason for update
            category: Reputation category
            action_id: Related action ID
            
        Returns:
            Updated reputation
        """
        update_data = {
            "score_delta": score_delta,
            "reason": reason,
            "category": category,
            "action_id": action_id
        }
        
        return self._request("POST", f"/reputation/agents/{agent_id}", update_data)
    
    def get_top_agents(self, category: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get top agents by reputation.
        
        Args:
            category: Reputation category
            limit: Number of agents to retrieve
            
        Returns:
            List of top agents
        """
        query = f"?limit={limit}"
        if category:
            query += f"&category={category}"
        
        return self._request("GET", f"/reputation/top{query}")


def main():
    """Run the sample client."""
    parser = argparse.ArgumentParser(description="ChaosCore API Gateway Sample Client")
    parser.add_argument("--url", default="http://localhost:8000", help="API Gateway URL")
    parser.add_argument("--agent-id", help="Agent ID for authentication")
    parser.add_argument("--key-file", help="Private key file for authentication")
    parser.add_argument("--register", action="store_true", help="Register a new agent")
    parser.add_argument("--name", help="Agent name for registration")
    parser.add_argument("--email", help="Agent email for registration")
    parser.add_argument("--action", help="Log an action")
    parser.add_argument("--description", help="Action description")
    
    args = parser.parse_args()
    
    # Create client
    client = ChaosGatewayClient(args.url)
    
    # Authenticate if agent ID and key file are provided
    if args.agent_id and args.key_file:
        with open(args.key_file, "r") as f:
            private_key = f.read()
        
        print(f"Authenticating as agent {args.agent_id}...")
        agent = client.authenticate(args.agent_id, private_key)
        print(f"Authenticated as {agent['name']} ({agent['id']})")
    
    # Register a new agent
    if args.register:
        if not args.name or not args.email:
            print("Error: --name and --email are required for registration")
            return
        
        print(f"Registering agent {args.name} ({args.email})...")
        agent = client.register_agent(args.name, args.email)
        print(f"Registered agent with ID: {agent['id']}")
    
    # Log an action
    if args.action and args.description:
        if not client.token:
            print("Error: Authentication required to log actions")
            return
        
        print(f"Logging action {args.action}...")
        action = client.log_action(args.action, args.description, {"sample": True})
        print(f"Logged action with ID: {action['id']}")


if __name__ == "__main__":
    main() 