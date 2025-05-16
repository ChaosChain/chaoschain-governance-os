"""
Proof of Agency module for ChaosCore.

This module provides interfaces and implementations for Proof of Agency.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any


class ProofOfAgencyInterface(ABC):
    """Interface for Proof of Agency implementations."""

    @abstractmethod
    def log_action(self, action_id: str, agent_id: str, action_type: str, description: Optional[str] = None, data: Optional[Dict[str, Any]] = None) -> str:
        """
        Log an action.
        
        Args:
            action_id: Action ID
            agent_id: Agent ID
            action_type: Action type
            description: Action description
            data: Action data
            
        Returns:
            Action ID
        """
        pass

    @abstractmethod
    def record_outcome(self, action_id: str, success: bool, results: Optional[Dict[str, Any]] = None, impact_score: float = 0.0) -> bool:
        """
        Record an action outcome.
        
        Args:
            action_id: Action ID
            success: Whether the action was successful
            results: Action results
            impact_score: Impact score
            
        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    def get_action(self, action_id: str) -> Optional[Dict[str, Any]]:
        """
        Get an action by ID.
        
        Args:
            action_id: Action ID
            
        Returns:
            Action data or None if not found
        """
        pass

    @abstractmethod
    def list_actions(self, agent_id: Optional[str] = None, action_type: Optional[str] = None, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        List actions.
        
        Args:
            agent_id: Filter by agent ID
            action_type: Filter by action type
            limit: Maximum number of actions to return
            offset: Offset for pagination
            
        Returns:
            List of actions
        """
        pass


# Import implementations
from chaoscore.core.database_adapter import PostgreSQLProofOfAgency

__all__ = ["ProofOfAgencyInterface", "PostgreSQLProofOfAgency"] 