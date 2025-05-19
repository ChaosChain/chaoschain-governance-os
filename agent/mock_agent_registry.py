"""
Mock Agent Registry

This module provides a mock agent registry for testing the governance analyst agent.
"""

import logging
import time
import uuid
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class MockAgentRegistry:
    """
    Mock agent registry for testing.
    
    In a production environment, this would be replaced with a full implementation
    that integrates with on-chain agent registry contracts.
    """
    
    def __init__(self):
        """Initialize the mock agent registry."""
        self.agents = {}
        self.registrations = {}
        logger.info("Initialized mock agent registry")
        
        # Initialize with some default agents
        self._initialize_default_agents()
    
    def _initialize_default_agents(self):
        """Initialize registry with some default agents."""
        default_agent_types = [
            "governance_analyst",
            "researcher",
            "developer",
            "validator",
            "executor"
        ]
        
        for agent_type in default_agent_types:
            agent_id = f"{agent_type}-{uuid.uuid4()}"
            self.register_agent(
                agent_id=agent_id,
                name=f"{agent_type.replace('_', ' ').title()} Agent",
                agent_type=agent_type,
                capabilities=[f"capability_{i}" for i in range(1, 4)],
                metadata={"default": True}
            )
    
    def register_agent(
        self,
        agent_id: str,
        name: str,
        agent_type: str,
        capabilities: List[str],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Register a new agent.
        
        Args:
            agent_id: Unique agent identifier
            name: Agent name
            agent_type: Type of agent
            capabilities: List of agent capabilities
            metadata: Additional agent metadata
            
        Returns:
            Registration details
        """
        timestamp = time.time()
        
        agent = {
            "id": agent_id,
            "name": name,
            "type": agent_type,
            "capabilities": capabilities,
            "metadata": metadata or {},
            "registered_at": timestamp,
            "updated_at": timestamp,
            "active": True
        }
        
        registration_id = f"registration-{uuid.uuid4()}"
        registration = {
            "id": registration_id,
            "agent_id": agent_id,
            "timestamp": timestamp
        }
        
        self.agents[agent_id] = agent
        self.registrations[registration_id] = registration
        
        logger.info(f"Registered agent: {agent_id} ({name}, {agent_type})")
        
        return registration
    
    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Get an agent by ID.
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Agent data or None if not found
        """
        return self.agents.get(agent_id)
    
    def is_registered(self, agent_id: str) -> bool:
        """
        Check if an agent is registered.
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Whether the agent is registered
        """
        return agent_id in self.agents and self.agents[agent_id]["active"]
    
    def update_agent(
        self,
        agent_id: str,
        name: Optional[str] = None,
        capabilities: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        active: Optional[bool] = None
    ) -> bool:
        """
        Update an agent's details.
        
        Args:
            agent_id: Agent ID
            name: New agent name
            capabilities: New agent capabilities
            metadata: New agent metadata
            active: New agent active status
            
        Returns:
            Whether the update was successful
        """
        if agent_id not in self.agents:
            logger.warning(f"Agent not found for update: {agent_id}")
            return False
        
        agent = self.agents[agent_id]
        
        if name is not None:
            agent["name"] = name
            
        if capabilities is not None:
            agent["capabilities"] = capabilities
            
        if metadata is not None:
            agent["metadata"] = metadata
            
        if active is not None:
            agent["active"] = active
            
        agent["updated_at"] = time.time()
        
        logger.info(f"Updated agent: {agent_id}")
        
        return True
    
    def deactivate_agent(self, agent_id: str) -> bool:
        """
        Deactivate an agent.
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Whether the deactivation was successful
        """
        return self.update_agent(agent_id, active=False)
    
    def get_agents_by_type(self, agent_type: str) -> List[Dict[str, Any]]:
        """
        Get all agents of a specific type.
        
        Args:
            agent_type: Agent type
            
        Returns:
            List of agents of the specified type
        """
        return [a for a in self.agents.values() if a["type"] == agent_type and a["active"]]
    
    def get_all_agents(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """
        Get all registered agents.
        
        Args:
            active_only: Whether to return only active agents
            
        Returns:
            List of agents
        """
        if active_only:
            return [a for a in self.agents.values() if a["active"]]
        return list(self.agents.values()) 