"""
Reputation System module for ChaosCore.

This module provides interfaces and implementations for the Reputation System.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any


class ReputationSystem(ABC):
    """Interface for Reputation System implementations."""

    @abstractmethod
    def get_reputation(self, agent_id: str, category: Optional[str] = None) -> float:
        """
        Get an agent's reputation score.
        
        Args:
            agent_id: Agent ID
            category: Reputation category
            
        Returns:
            Reputation score
        """
        pass

    @abstractmethod
    def update_reputation(self, agent_id: str, score_delta: float, category: Optional[str] = None, reason: Optional[str] = None, action_id: Optional[str] = None) -> bool:
        """
        Update an agent's reputation.
        
        Args:
            agent_id: Agent ID
            score_delta: Score delta
            category: Reputation category
            reason: Reason for update
            action_id: Related action ID
            
        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    def get_history(self, agent_id: str, category: Optional[str] = None, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get an agent's reputation history.
        
        Args:
            agent_id: Agent ID
            category: Reputation category
            limit: Maximum number of history entries to return
            offset: Offset for pagination
            
        Returns:
            List of history entries
        """
        pass

    @abstractmethod
    def get_top_agents(self, category: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get top agents by reputation.
        
        Args:
            category: Reputation category
            limit: Maximum number of agents to return
            
        Returns:
            List of top agents
        """
        pass


# Import implementations
from chaoscore.core.database_adapter import PostgreSQLReputationSystem

__all__ = ["ReputationSystem", "PostgreSQLReputationSystem"] 