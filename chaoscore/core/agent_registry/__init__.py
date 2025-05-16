"""
Agent Registry module for ChaosCore.

This module provides interfaces and implementations for the Agent Registry.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any


class AgentRegistryInterface(ABC):
    """Interface for Agent Registry implementations."""

    @abstractmethod
    def create_agent(self, agent_id: str, name: str, email: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a new agent.
        
        Args:
            agent_id: Agent ID
            name: Agent name
            email: Agent email
            metadata: Agent metadata
            
        Returns:
            Agent ID
        """
        pass

    @abstractmethod
    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Get an agent by ID.
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Agent data or None if not found
        """
        pass

    @abstractmethod
    def list_agents(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        List agents.
        
        Args:
            limit: Maximum number of agents to return
            offset: Offset for pagination
            
        Returns:
            List of agents
        """
        pass

    @abstractmethod
    def update_agent(self, agent_id: str, name: Optional[str] = None, email: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Update an agent.
        
        Args:
            agent_id: Agent ID
            name: New agent name
            email: New agent email
            metadata: New agent metadata
            
        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    def delete_agent(self, agent_id: str) -> bool:
        """
        Delete an agent.
        
        Args:
            agent_id: Agent ID
            
        Returns:
            True if successful, False otherwise
        """
        pass


# Import implementations
from chaoscore.core.database_adapter import PostgreSQLAgentRegistry

__all__ = ["AgentRegistryInterface", "PostgreSQLAgentRegistry"] 