"""
Reputation System Interfaces

This module defines the interfaces for the Reputation System.
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple


class ReputationScore:
    """
    Represents a reputation score for an agent.
    
    A reputation score includes the overall score, component scores,
    and metadata about when and how the score was computed.
    """
    
    def get_agent_id(self) -> str:
        """Get the ID of the agent this score belongs to."""
        pass
    
    def get_overall_score(self) -> float:
        """Get the overall reputation score (0-100)."""
        pass
    
    def get_component_scores(self) -> Dict[str, float]:
        """
        Get the component scores.
        
        Components may include:
        - action_quality: Quality of actions performed
        - verification_accuracy: Accuracy of verifications
        - consistency: Consistency of performance
        - etc.
        
        Returns:
            Dict[str, float]: Component scores (0-100)
        """
        pass
    
    def get_timestamp(self) -> datetime:
        """Get the timestamp when this score was computed."""
        pass
    
    def get_computation_details(self) -> Dict[str, Any]:
        """Get details about how this score was computed."""
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the reputation score to a dictionary."""
        pass
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ReputationScore':
        """Create a reputation score from a dictionary."""
        pass


class ReputationQueryInterface(ABC):
    """
    Interface for querying reputation scores.
    
    This interface provides methods for querying reputation scores
    for agents in the ChaosCore platform.
    """
    
    @abstractmethod
    def get_reputation(self, agent_id: str) -> Optional[ReputationScore]:
        """
        Get the reputation score for an agent.
        
        Args:
            agent_id: The ID of the agent
            
        Returns:
            Optional[ReputationScore]: The reputation score, or None if not found
        """
        pass
    
    @abstractmethod
    def get_top_agents(self, limit: int = 10, category: Optional[str] = None) -> List[Tuple[str, float]]:
        """
        Get the top agents by reputation score.
        
        Args:
            limit: The maximum number of agents to return
            category: Optional category to filter by
            
        Returns:
            List[Tuple[str, float]]: A list of (agent_id, score) tuples
        """
        pass
    
    @abstractmethod
    def get_reputation_history(self, agent_id: str, limit: int = 10) -> List[ReputationScore]:
        """
        Get the reputation history for an agent.
        
        Args:
            agent_id: The ID of the agent
            limit: The maximum number of history entries to return
            
        Returns:
            List[ReputationScore]: A list of historical reputation scores
        """
        pass


class ReputationComputeInterface(ABC):
    """
    Interface for computing reputation scores.
    
    This interface provides methods for computing reputation scores
    for agents in the ChaosCore platform.
    """
    
    @abstractmethod
    def compute_reputation(self, agent_id: str) -> ReputationScore:
        """
        Compute the reputation score for an agent.
        
        This method computes the reputation score for an agent based on
        their actions, verifications, and other factors.
        
        Args:
            agent_id: The ID of the agent
            
        Returns:
            ReputationScore: The computed reputation score
        """
        pass
    
    @abstractmethod
    def update_all_reputations(self) -> Dict[str, float]:
        """
        Update reputation scores for all agents.
        
        This method computes and stores reputation scores for all agents
        in the system.
        
        Returns:
            Dict[str, float]: A dictionary mapping agent IDs to their new overall scores
        """
        pass 