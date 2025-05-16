"""
Unit tests for the Reputation System.
"""
import pytest
from datetime import datetime
from unittest.mock import MagicMock

from chaoscore.core.agent_registry import AgentRegistryInterface
from chaoscore.core.proof_of_agency import ProofOfAgencyInterface, ActionStatus
from chaoscore.core.reputation import (
    ReputationScore,
    StandardReputationScore,
    InMemoryReputationSystem
)


class TestStandardReputationScore:
    """Test the StandardReputationScore implementation"""
    
    def test_init_and_getters(self):
        """Test initialization and getter methods"""
        agent_id = "test_agent_123"
        overall_score = 85.5
        component_scores = {
            "action_quality": 90.0,
            "verification": 80.0,
            "consistency": 85.0
        }
        timestamp = datetime.now()
        computation_details = {
            "method": "weighted_average",
            "weights": {
                "action_quality": 0.5,
                "verification": 0.3,
                "consistency": 0.2
            }
        }
        
        score = StandardReputationScore(
            agent_id=agent_id,
            overall_score=overall_score,
            component_scores=component_scores,
            timestamp=timestamp,
            computation_details=computation_details
        )
        
        assert score.get_agent_id() == agent_id
        assert score.get_overall_score() == overall_score
        assert score.get_component_scores() == component_scores
        assert score.get_timestamp() == timestamp
        assert score.get_computation_details() == computation_details
    
    def test_to_dict_and_from_dict(self):
        """Test to_dict and from_dict methods"""
        original = StandardReputationScore(
            agent_id="test_agent_123",
            overall_score=85.5,
            component_scores={
                "action_quality": 90.0,
                "verification": 80.0,
                "consistency": 85.0
            },
            timestamp=datetime.fromisoformat("2023-01-01T12:00:00"),
            computation_details={
                "method": "weighted_average",
                "weights": {
                    "action_quality": 0.5,
                    "verification": 0.3,
                    "consistency": 0.2
                }
            }
        )
        
        # Convert to dict and back
        score_dict = original.to_dict()
        reconstructed = StandardReputationScore.from_dict(score_dict)
        
        # Verify all properties are preserved
        assert original.get_agent_id() == reconstructed.get_agent_id()
        assert original.get_overall_score() == reconstructed.get_overall_score()
        assert original.get_component_scores() == reconstructed.get_component_scores()
        assert original.get_timestamp().isoformat() == reconstructed.get_timestamp().isoformat()
        assert original.get_computation_details() == reconstructed.get_computation_details()


class TestInMemoryReputationSystem:
    """Test the InMemoryReputationSystem implementation"""
    
    @pytest.fixture
    def mock_agent_registry(self):
        """Create a mock agent registry"""
        registry = MagicMock(spec=AgentRegistryInterface)
        
        # Configure list_agents to return a list of agent IDs
        registry.list_agents.return_value = ["agent_1", "agent_2", "agent_3"]
        
        # Configure get_agent to return a mock agent for valid IDs
        def get_agent_side_effect(agent_id):
            if agent_id in ["agent_1", "agent_2", "agent_3"]:
                return MagicMock(name=f"Mock Agent {agent_id}")
            return None
        
        registry.get_agent.side_effect = get_agent_side_effect
        return registry
    
    @pytest.fixture
    def mock_proof_of_agency(self):
        """Create a mock proof of agency"""
        poa = MagicMock(spec=ProofOfAgencyInterface)
        
        # Configure list_actions to return actions for agent_1
        def list_actions_side_effect(agent_id=None, action_type=None):
            if agent_id == "agent_1":
                return ["action_1", "action_2", "action_3"]
            elif agent_id == "agent_2":
                return ["action_4", "action_5"]
            elif agent_id == "agent_3":
                return []
            else:
                return ["action_1", "action_2", "action_3", "action_4", "action_5"]
        
        poa.list_actions.side_effect = list_actions_side_effect
        
        # Configure get_action to return mock actions
        def get_action_side_effect(action_id):
            action = MagicMock()
            action.get_agent_id.return_value = {
                "action_1": "agent_1",
                "action_2": "agent_1",
                "action_3": "agent_1",
                "action_4": "agent_2",
                "action_5": "agent_2"
            }.get(action_id)
            
            action.get_status.return_value = MagicMock(
                name=ActionStatus.COMPLETED
            )
            
            action.get_verification_data = lambda: {
                "action_1": {"verifier_id": "agent_2"},
                "action_2": {"verifier_id": "agent_2"},
                "action_3": {"verifier_id": "agent_3"},
                "action_4": {"verifier_id": "agent_1"},
                "action_5": {"verifier_id": "agent_1"}
            }.get(action_id)
            
            return action
        
        poa.get_action.side_effect = get_action_side_effect
        
        # Configure get_outcome to return mock outcomes
        def get_outcome_side_effect(action_id):
            outcome = MagicMock()
            outcome.get_success.return_value = action_id != "action_3"
            outcome.get_impact_score.return_value = {
                "action_1": 0.9,
                "action_2": 0.8,
                "action_3": 0.5,
                "action_4": 0.7,
                "action_5": 0.6
            }.get(action_id)
            
            return outcome
        
        poa.get_outcome.side_effect = get_outcome_side_effect
        
        return poa
    
    @pytest.fixture
    def reputation_system(self, mock_agent_registry, mock_proof_of_agency):
        """Create a reputation system with mock dependencies"""
        return InMemoryReputationSystem(mock_agent_registry, mock_proof_of_agency)
    
    def test_compute_reputation(self, reputation_system):
        """Test computing reputation for an agent"""
        # Compute reputation for agent_1
        score = reputation_system.compute_reputation("agent_1")
        
        # Verify the score
        assert score.get_agent_id() == "agent_1"
        assert score.get_overall_score() > 0
        assert "action_quality" in score.get_component_scores()
        assert "verification" in score.get_component_scores()
        assert "consistency" in score.get_component_scores()
        assert score.get_timestamp() is not None
        assert score.get_computation_details() is not None
    
    def test_get_reputation(self, reputation_system):
        """Test getting reputation for an agent"""
        # Compute reputation for agent_1 (to store it)
        reputation_system.compute_reputation("agent_1")
        
        # Get the reputation
        score = reputation_system.get_reputation("agent_1")
        
        # Verify the score is returned
        assert score is not None
        assert score.get_agent_id() == "agent_1"
        
        # Test getting reputation for an agent with no score
        score = reputation_system.get_reputation("non_existent_agent")
        assert score is None
    
    def test_get_top_agents(self, reputation_system):
        """Test getting top agents by reputation"""
        # Compute reputation for all agents
        reputation_system.update_all_reputations()
        
        # Get top 2 agents
        top_agents = reputation_system.get_top_agents(limit=2)
        
        # Verify the result
        assert len(top_agents) == 2
        assert isinstance(top_agents[0], tuple)
        assert isinstance(top_agents[0][0], str)
        assert isinstance(top_agents[0][1], float)
        
        # Verify agents are sorted by score
        assert top_agents[0][1] >= top_agents[1][1]
    
    def test_get_reputation_history(self, reputation_system):
        """Test getting reputation history for an agent"""
        # Compute reputation for agent_1 multiple times
        reputation_system.compute_reputation("agent_1")
        reputation_system.compute_reputation("agent_1")
        
        # Get the reputation history
        history = reputation_system.get_reputation_history("agent_1")
        
        # Verify the history
        assert len(history) == 2
        assert all(isinstance(score, ReputationScore) for score in history)
        assert all(score.get_agent_id() == "agent_1" for score in history)
    
    def test_update_all_reputations(self, reputation_system, mock_agent_registry):
        """Test updating reputation for all agents"""
        # Update all reputations
        results = reputation_system.update_all_reputations()
        
        # Verify the results
        assert len(results) == 3
        assert all(agent_id in results for agent_id in ["agent_1", "agent_2", "agent_3"])
        assert all(isinstance(score, float) for score in results.values()) 