"""
Reputation System Implementations

This module provides implementations of the Reputation System interfaces.
"""
import uuid
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy.orm import Session

from chaoscore.core.common.db import get_db
from chaoscore.core.agent_registry import AgentRegistryInterface
from chaoscore.core.proof_of_agency import ProofOfAgencyInterface, ActionType

from .interfaces import (
    ReputationScore,
    ReputationQueryInterface,
    ReputationComputeInterface
)
from .models import ReputationScoreModel, ReputationHistoryModel


class StandardReputationScore(ReputationScore):
    """
    Standard implementation of ReputationScore.
    """
    
    def __init__(
        self,
        agent_id: str,
        overall_score: float,
        component_scores: Dict[str, float],
        timestamp: datetime,
        computation_details: Optional[Dict[str, Any]] = None
    ):
        self._agent_id = agent_id
        self._overall_score = overall_score
        self._component_scores = component_scores
        self._timestamp = timestamp
        self._computation_details = computation_details or {}
    
    def get_agent_id(self) -> str:
        return self._agent_id
    
    def get_overall_score(self) -> float:
        return self._overall_score
    
    def get_component_scores(self) -> Dict[str, float]:
        return self._component_scores.copy()
    
    def get_timestamp(self) -> datetime:
        return self._timestamp
    
    def get_computation_details(self) -> Dict[str, Any]:
        return self._computation_details.copy()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self._agent_id,
            "overall_score": self._overall_score,
            "component_scores": self._component_scores,
            "timestamp": self._timestamp.isoformat(),
            "computation_details": self._computation_details
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StandardReputationScore':
        return cls(
            agent_id=data["agent_id"],
            overall_score=data["overall_score"],
            component_scores=data["component_scores"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            computation_details=data.get("computation_details", {})
        )
    
    @classmethod
    def from_model(cls, model: ReputationScoreModel) -> 'StandardReputationScore':
        """
        Create a StandardReputationScore from a ReputationScoreModel.
        
        Args:
            model: The ReputationScoreModel
            
        Returns:
            StandardReputationScore: The reputation score
        """
        return cls(
            agent_id=model.agent_id,
            overall_score=model.overall_score,
            component_scores=model.component_scores,
            timestamp=model.timestamp,
            computation_details=model.computation_details
        )


class BaseReputationComputer:
    """
    Base class for reputation computers.
    
    This class provides common functionality for computing reputation scores.
    """
    
    def __init__(
        self,
        agent_registry: AgentRegistryInterface,
        proof_of_agency: ProofOfAgencyInterface
    ):
        self._agent_registry = agent_registry
        self._proof_of_agency = proof_of_agency
    
    def _compute_action_quality_score(self, agent_id: str) -> float:
        """
        Compute the action quality score for an agent.
        
        Args:
            agent_id: The ID of the agent
            
        Returns:
            float: The action quality score (0-100)
        """
        # Get all actions for the agent
        action_ids = self._proof_of_agency.list_actions(agent_id=agent_id)
        
        if not action_ids:
            return 0.0
        
        total_score = 0.0
        completed_count = 0
        
        for action_id in action_ids:
            action = self._proof_of_agency.get_action(action_id)
            
            # Only consider completed actions
            if action.get_status().name != "COMPLETED":
                continue
            
            # Get the outcome for the action
            outcome = self._proof_of_agency.get_outcome(action_id)
            if outcome:
                # Use impact score if available
                impact_score = outcome.get_impact_score() or 0.0
                total_score += impact_score * 100  # Convert to 0-100 scale
                completed_count += 1
        
        # Calculate average score
        if completed_count > 0:
            return total_score / completed_count
        else:
            return 0.0
    
    def _compute_verification_score(self, agent_id: str) -> float:
        """
        Compute the verification score for an agent.
        
        Args:
            agent_id: The ID of the agent
            
        Returns:
            float: The verification score (0-100)
        """
        # Get all actions verified by the agent
        # This is a simplification - in a real system, we would need to track verifications
        # For now, we'll just check actions where this agent is mentioned in verification data
        
        all_action_ids = self._proof_of_agency.list_actions()
        verification_count = 0
        
        for action_id in all_action_ids:
            action = self._proof_of_agency.get_action(action_id)
            
            # Check if this agent performed the verification
            if getattr(action, "get_verification_data", None):
                verification_data = action.get_verification_data()
                if verification_data and verification_data.get("verifier_id") == agent_id:
                    verification_count += 1
        
        # Simple scoring based on verification count
        if verification_count > 10:
            return 100.0
        elif verification_count > 0:
            return verification_count * 10.0
        else:
            return 0.0
    
    def _compute_consistency_score(self, agent_id: str) -> float:
        """
        Compute the consistency score for an agent.
        
        Args:
            agent_id: The ID of the agent
            
        Returns:
            float: The consistency score (0-100)
        """
        # Get all actions for the agent
        action_ids = self._proof_of_agency.list_actions(agent_id=agent_id)
        
        if not action_ids:
            return 0.0
        
        # Count successful actions
        successful_count = 0
        
        for action_id in action_ids:
            outcome = self._proof_of_agency.get_outcome(action_id)
            if outcome and outcome.get_success():
                successful_count += 1
        
        # Calculate success rate
        if action_ids:
            success_rate = successful_count / len(action_ids)
            return success_rate * 100.0
        else:
            return 0.0


class SqlReputationSystem(ReputationQueryInterface, ReputationComputeInterface, BaseReputationComputer):
    """
    SQL-backed implementation of the Reputation System.
    
    This implementation stores reputation scores in a SQL database.
    """
    
    def __init__(
        self,
        agent_registry: AgentRegistryInterface,
        proof_of_agency: ProofOfAgencyInterface,
        db: Optional[Session] = None
    ):
        super().__init__(agent_registry, proof_of_agency)
        self._db = db
    
    def _get_db(self) -> Session:
        """
        Get a database session.
        
        Returns:
            Session: A database session
        """
        if self._db:
            return self._db
        else:
            # Create a new session
            return next(get_db())
    
    def get_reputation(self, agent_id: str) -> Optional[ReputationScore]:
        """
        Get the reputation score for an agent.
        
        Args:
            agent_id: The ID of the agent
            
        Returns:
            Optional[ReputationScore]: The reputation score, or None if not found
        """
        db = self._get_db()
        
        # Query for the most recent reputation score
        score_model = db.query(ReputationScoreModel) \
            .filter(ReputationScoreModel.agent_id == agent_id) \
            .order_by(ReputationScoreModel.timestamp.desc()) \
            .first()
        
        if score_model:
            return StandardReputationScore.from_model(score_model)
        else:
            return None
    
    def get_top_agents(self, limit: int = 10, category: Optional[str] = None) -> List[Tuple[str, float]]:
        """
        Get the top agents by reputation score.
        
        Args:
            limit: The maximum number of agents to return
            category: Optional category to filter by
            
        Returns:
            List[Tuple[str, float]]: A list of (agent_id, score) tuples
        """
        db = self._get_db()
        
        # Query for top agents
        query = db.query(ReputationScoreModel.agent_id, ReputationScoreModel.overall_score) \
            .order_by(ReputationScoreModel.overall_score.desc()) \
            .limit(limit)
        
        # Convert to list of tuples
        return [(row.agent_id, row.overall_score) for row in query]
    
    def get_reputation_history(self, agent_id: str, limit: int = 10) -> List[ReputationScore]:
        """
        Get the reputation history for an agent.
        
        Args:
            agent_id: The ID of the agent
            limit: The maximum number of history entries to return
            
        Returns:
            List[ReputationScore]: A list of historical reputation scores
        """
        db = self._get_db()
        
        # Query for reputation history
        history_models = db.query(ReputationHistoryModel) \
            .filter(ReputationHistoryModel.agent_id == agent_id) \
            .order_by(ReputationHistoryModel.timestamp.desc()) \
            .limit(limit) \
            .all()
        
        # Convert to ReputationScore objects
        return [
            StandardReputationScore(
                agent_id=model.agent_id,
                overall_score=model.overall_score,
                component_scores=model.component_scores,
                timestamp=model.timestamp,
                computation_details={}
            )
            for model in history_models
        ]
    
    def compute_reputation(self, agent_id: str) -> ReputationScore:
        """
        Compute the reputation score for an agent.
        
        Args:
            agent_id: The ID of the agent
            
        Returns:
            ReputationScore: The computed reputation score
        """
        # Compute component scores
        action_quality = self._compute_action_quality_score(agent_id)
        verification_score = self._compute_verification_score(agent_id)
        consistency_score = self._compute_consistency_score(agent_id)
        
        # Compute overall score (weighted average)
        overall_score = (
            action_quality * 0.5 +
            verification_score * 0.3 +
            consistency_score * 0.2
        )
        
        # Create component scores dictionary
        component_scores = {
            "action_quality": action_quality,
            "verification": verification_score,
            "consistency": consistency_score
        }
        
        # Create computation details
        computation_details = {
            "timestamp": datetime.utcnow().isoformat(),
            "method": "weighted_average",
            "weights": {
                "action_quality": 0.5,
                "verification": 0.3,
                "consistency": 0.2
            }
        }
        
        # Create reputation score
        score = StandardReputationScore(
            agent_id=agent_id,
            overall_score=overall_score,
            component_scores=component_scores,
            timestamp=datetime.utcnow(),
            computation_details=computation_details
        )
        
        # Save to database
        self._save_reputation(score)
        
        return score
    
    def update_all_reputations(self) -> Dict[str, float]:
        """
        Update reputation scores for all agents.
        
        Returns:
            Dict[str, float]: A dictionary mapping agent IDs to their new overall scores
        """
        # Get all agent IDs
        all_agents = self._agent_registry.list_agents()
        
        results = {}
        
        # Compute reputation for each agent
        for agent_id in all_agents:
            score = self.compute_reputation(agent_id)
            results[agent_id] = score.get_overall_score()
        
        return results
    
    def _save_reputation(self, score: ReputationScore) -> None:
        """
        Save a reputation score to the database.
        
        Args:
            score: The reputation score to save
        """
        db = self._get_db()
        
        # Create model
        model = ReputationScoreModel(
            agent_id=score.get_agent_id(),
            overall_score=score.get_overall_score(),
            component_scores=score.get_component_scores(),
            timestamp=score.get_timestamp(),
            computation_details=score.get_computation_details()
        )
        
        # Add to database
        db.add(model)
        db.commit()
        
        # Create history entry
        history_model = ReputationHistoryModel(
            score_id=model.id,
            agent_id=score.get_agent_id(),
            overall_score=score.get_overall_score(),
            component_scores=score.get_component_scores(),
            timestamp=score.get_timestamp()
        )
        
        # Add to database
        db.add(history_model)
        db.commit()


class InMemoryReputationSystem(ReputationQueryInterface, ReputationComputeInterface, BaseReputationComputer):
    """
    In-memory implementation of the Reputation System.
    
    This implementation stores reputation scores in memory.
    """
    
    def __init__(
        self,
        agent_registry: AgentRegistryInterface,
        proof_of_agency: ProofOfAgencyInterface
    ):
        super().__init__(agent_registry, proof_of_agency)
        self._scores = {}  # agent_id -> ReputationScore
        self._history = {}  # agent_id -> List[ReputationScore]
    
    def get_reputation(self, agent_id: str) -> Optional[ReputationScore]:
        """
        Get the reputation score for an agent.
        
        Args:
            agent_id: The ID of the agent
            
        Returns:
            Optional[ReputationScore]: The reputation score, or None if not found
        """
        return self._scores.get(agent_id)
    
    def get_top_agents(self, limit: int = 10, category: Optional[str] = None) -> List[Tuple[str, float]]:
        """
        Get the top agents by reputation score.
        
        Args:
            limit: The maximum number of agents to return
            category: Optional category to filter by
            
        Returns:
            List[Tuple[str, float]]: A list of (agent_id, score) tuples
        """
        # Sort agents by score
        sorted_agents = sorted(
            self._scores.items(),
            key=lambda item: item[1].get_overall_score(),
            reverse=True
        )
        
        # Take top N
        return [(agent_id, score.get_overall_score()) for agent_id, score in sorted_agents[:limit]]
    
    def get_reputation_history(self, agent_id: str, limit: int = 10) -> List[ReputationScore]:
        """
        Get the reputation history for an agent.
        
        Args:
            agent_id: The ID of the agent
            limit: The maximum number of history entries to return
            
        Returns:
            List[ReputationScore]: A list of historical reputation scores
        """
        history = self._history.get(agent_id, [])
        
        # Sort by timestamp (newest first)
        sorted_history = sorted(
            history,
            key=lambda score: score.get_timestamp(),
            reverse=True
        )
        
        return sorted_history[:limit]
    
    def compute_reputation(self, agent_id: str) -> ReputationScore:
        """
        Compute the reputation score for an agent.
        
        Args:
            agent_id: The ID of the agent
            
        Returns:
            ReputationScore: The computed reputation score
        """
        # Compute component scores
        action_quality = self._compute_action_quality_score(agent_id)
        verification_score = self._compute_verification_score(agent_id)
        consistency_score = self._compute_consistency_score(agent_id)
        
        # Compute overall score (weighted average)
        overall_score = (
            action_quality * 0.5 +
            verification_score * 0.3 +
            consistency_score * 0.2
        )
        
        # Create component scores dictionary
        component_scores = {
            "action_quality": action_quality,
            "verification": verification_score,
            "consistency": consistency_score
        }
        
        # Create computation details
        computation_details = {
            "timestamp": datetime.utcnow().isoformat(),
            "method": "weighted_average",
            "weights": {
                "action_quality": 0.5,
                "verification": 0.3,
                "consistency": 0.2
            }
        }
        
        # Create reputation score
        score = StandardReputationScore(
            agent_id=agent_id,
            overall_score=overall_score,
            component_scores=component_scores,
            timestamp=datetime.utcnow(),
            computation_details=computation_details
        )
        
        # Save to memory
        self._scores[agent_id] = score
        
        # Add to history
        if agent_id not in self._history:
            self._history[agent_id] = []
        self._history[agent_id].append(score)
        
        return score
    
    def update_all_reputations(self) -> Dict[str, float]:
        """
        Update reputation scores for all agents.
        
        Returns:
            Dict[str, float]: A dictionary mapping agent IDs to their new overall scores
        """
        # Get all agent IDs
        all_agents = self._agent_registry.list_agents()
        
        results = {}
        
        # Compute reputation for each agent
        for agent_id in all_agents:
            score = self.compute_reputation(agent_id)
            results[agent_id] = score.get_overall_score()
        
        return results 