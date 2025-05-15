"""
Reputation Adapter Implementation

This module implements the adapter for connecting the governance system to the ChaosCore
Reputation System.
"""
from typing import Dict, Any, Optional, List, Tuple

from chaoscore.core.reputation import (
    ReputationQueryInterface,
    ReputationComputeInterface,
    ReputationScore
)


class ReputationAdapter:
    """
    Adapter for the ChaosCore Reputation System.
    
    This adapter provides methods for querying and computing reputation scores
    using the ChaosCore Reputation System interfaces.
    """
    
    def __init__(self, reputation_system):
        """
        Initialize the reputation adapter.
        
        Args:
            reputation_system: ChaosCore Reputation System implementation
                (must implement both ReputationQueryInterface and ReputationComputeInterface)
        """
        self._reputation_system = reputation_system
    
    def get_agent_reputation(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the reputation score for an agent.
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            Dict[str, Any]: Reputation data if found, None otherwise
        """
        score = self._reputation_system.get_reputation(agent_id)
        if score:
            return {
                "agent_id": score.get_agent_id(),
                "overall_score": score.get_overall_score(),
                "component_scores": score.get_component_scores(),
                "timestamp": score.get_timestamp().isoformat(),
                "details": score.get_computation_details()
            }
        return None
    
    def compute_agent_reputation(self, agent_id: str) -> Dict[str, Any]:
        """
        Compute the reputation score for an agent.
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            Dict[str, Any]: Computed reputation data
        """
        score = self._reputation_system.compute_reputation(agent_id)
        return {
            "agent_id": score.get_agent_id(),
            "overall_score": score.get_overall_score(),
            "component_scores": score.get_component_scores(),
            "timestamp": score.get_timestamp().isoformat(),
            "details": score.get_computation_details()
        }
    
    def get_top_agents(self, limit: int = 10, category: Optional[str] = None) -> List[Tuple[str, float]]:
        """
        Get the top agents by reputation score.
        
        Args:
            limit: Maximum number of agents to return
            category: Optional category to filter by
            
        Returns:
            List[Tuple[str, float]]: List of (agent_id, score) tuples
        """
        return self._reputation_system.get_top_agents(limit=limit, category=category)
    
    def get_agent_reputation_history(self, agent_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the reputation history for an agent.
        
        Args:
            agent_id: ID of the agent
            limit: Maximum number of history entries to return
            
        Returns:
            List[Dict[str, Any]]: List of historical reputation data
        """
        history = self._reputation_system.get_reputation_history(agent_id, limit=limit)
        return [
            {
                "agent_id": score.get_agent_id(),
                "overall_score": score.get_overall_score(),
                "component_scores": score.get_component_scores(),
                "timestamp": score.get_timestamp().isoformat()
            }
            for score in history
        ]
    
    def update_all_reputations(self) -> Dict[str, float]:
        """
        Update reputation scores for all agents.
        
        Returns:
            Dict[str, float]: Dictionary mapping agent IDs to their new overall scores
        """
        return self._reputation_system.update_all_reputations()
    
    def update_agent_reputation_after_action(self, agent_id: str, action_id: str) -> Dict[str, Any]:
        """
        Update an agent's reputation after they perform an action.
        
        This is a convenience method that computes a new reputation score for an agent
        and returns the delta from their previous score.
        
        Args:
            agent_id: ID of the agent
            action_id: ID of the action that triggered the update
            
        Returns:
            Dict[str, Any]: Reputation update data including before/after scores and delta
        """
        # Get current reputation (before update)
        before_score = self._reputation_system.get_reputation(agent_id)
        before_overall = 0
        if before_score:
            before_overall = before_score.get_overall_score()
        
        # Compute new reputation
        after_score = self._reputation_system.compute_reputation(agent_id)
        after_overall = after_score.get_overall_score()
        
        # Calculate delta
        delta = after_overall - before_overall
        
        return {
            "agent_id": agent_id,
            "action_id": action_id,
            "before_score": before_overall,
            "after_score": after_overall,
            "delta": delta,
            "component_scores": after_score.get_component_scores(),
            "timestamp": after_score.get_timestamp().isoformat()
        } 