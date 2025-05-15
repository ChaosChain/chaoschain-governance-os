"""
Integration tests for the Reputation System with Agent Registry and Proof of Agency.
"""
import pytest
from datetime import datetime

from chaoscore.core.agent_registry import InMemoryAgentRegistry
from chaoscore.core.proof_of_agency import (
    ActionType,
    ActionStatus,
    InMemoryProofOfAgency
)
from chaoscore.core.reputation import InMemoryReputationSystem


@pytest.fixture
def setup_components():
    """Set up the components needed for testing."""
    # Create an agent registry
    agent_registry = InMemoryAgentRegistry()
    
    # Register test agents
    agent1_id = agent_registry.register_agent(
        "agent1@example.com", 
        "Agent One", 
        {"role": "analyzer", "capabilities": ["data_analysis", "prediction"]}
    )
    
    agent2_id = agent_registry.register_agent(
        "agent2@example.com", 
        "Agent Two", 
        {"role": "verifier", "capabilities": ["verification", "validation"]}
    )
    
    # Create a Proof of Agency instance
    poa = InMemoryProofOfAgency(agent_registry)
    
    # Create a Reputation System instance
    reputation = InMemoryReputationSystem(agent_registry, poa)
    
    return agent_registry, poa, reputation, agent1_id, agent2_id


def test_end_to_end_flow(setup_components):
    """Test the complete flow from agent registration to reputation calculation."""
    registry, poa, reputation, agent1_id, agent2_id = setup_components
    
    # Step 1: Record actions for agent1
    action1_id = poa.log_action(
        agent_id=agent1_id,
        action_type=ActionType.ANALYZE,
        description="Comprehensive market analysis",
        data={"market": "crypto", "timeframe": "1d", "indicators": ["RSI", "MACD"]}
    )
    
    action2_id = poa.log_action(
        agent_id=agent1_id,
        action_type=ActionType.CREATE,
        description="Generate trading strategy",
        data={"strategy_type": "momentum", "risk_level": "medium"}
    )
    
    # Step 2: Verify actions by agent2
    poa.verify_action(action1_id, agent2_id)
    poa.verify_action(action2_id, agent2_id)
    
    # Step 3: Anchor the actions
    poa.anchor_action(action1_id)
    poa.anchor_action(action2_id)
    
    # Step 4: Record outcomes
    poa.record_outcome(
        action_id=action1_id,
        success=True,
        impact_score=0.9,
        results={"prediction_accuracy": 0.92, "recommendations": ["buy", "hold", "sell"]}
    )
    
    poa.record_outcome(
        action_id=action2_id,
        success=True,
        impact_score=0.8,
        results={"strategy_performance": 0.85, "win_rate": 0.75}
    )
    
    # Step 5: Record an action for agent2
    action3_id = poa.log_action(
        agent_id=agent2_id,
        action_type=ActionType.VERIFY,
        description="Verify trading strategy",
        data={"strategy_id": "momentum_001", "verification_method": "backtest"}
    )
    
    # Step 6: Verify action by agent1
    poa.verify_action(action3_id, agent1_id)
    
    # Step 7: Anchor the action
    poa.anchor_action(action3_id)
    
    # Step 8: Record outcome
    poa.record_outcome(
        action_id=action3_id,
        success=True,
        impact_score=0.7,
        results={"verification_accuracy": 0.95, "issues_found": 2}
    )
    
    # Step 9: Compute reputation for both agents
    agent1_score = reputation.compute_reputation(agent1_id)
    agent2_score = reputation.compute_reputation(agent2_id)
    
    # Verify the scores
    assert agent1_score is not None
    assert agent1_score.get_agent_id() == agent1_id
    assert agent1_score.get_overall_score() > 0
    
    assert agent2_score is not None
    assert agent2_score.get_agent_id() == agent2_id
    assert agent2_score.get_overall_score() > 0
    
    # Step 10: Get top agents
    top_agents = reputation.get_top_agents()
    
    # Verify the top agents
    assert len(top_agents) == 2  # We only have 2 agents
    assert all(agent_id in [agent1_id, agent2_id] for agent_id, _ in top_agents)


def test_compute_reputation_after_completing_action(setup_components):
    """Test computing reputation immediately after completing an action."""
    registry, poa, reputation, agent1_id, agent2_id = setup_components
    
    # Step 1: Record an action
    action_id = poa.log_action(
        agent_id=agent1_id,
        action_type=ActionType.ANALYZE,
        description="Data analysis",
        data={"dataset": "weather", "method": "regression"}
    )
    
    # Step 2: Get initial reputation (should be very low as no completed actions)
    initial_score = reputation.compute_reputation(agent1_id)
    initial_overall = initial_score.get_overall_score()
    
    # Step 3: Complete the action flow
    poa.verify_action(action_id, agent2_id)
    poa.anchor_action(action_id)
    
    poa.record_outcome(
        action_id=action_id,
        success=True,
        impact_score=0.95,
        results={"accuracy": 0.98}
    )
    
    # Step 4: Get updated reputation
    updated_score = reputation.compute_reputation(agent1_id)
    updated_overall = updated_score.get_overall_score()
    
    # Verify the reputation increased
    assert updated_overall > initial_overall
    
    # Step 5: Check action_quality specifically
    component_scores = updated_score.get_component_scores()
    assert component_scores["action_quality"] > 0


def test_reputation_history(setup_components):
    """Test the reputation history functionality."""
    registry, poa, reputation, agent1_id, agent2_id = setup_components
    
    # Step 1: Compute reputation multiple times
    for _ in range(3):
        # Record and complete an action in between to change the reputation
        action_id = poa.log_action(
            agent_id=agent1_id,
            action_type=ActionType.ANALYZE,
            description=f"Analysis {_}",
            data={"iteration": _}
        )
        
        poa.verify_action(action_id, agent2_id)
        poa.anchor_action(action_id)
        
        poa.record_outcome(
            action_id=action_id,
            success=True,
            impact_score=0.8 + (_ * 0.05),  # Increasing score
            results={"result": f"result_{_}"}
        )
        
        # Compute reputation
        reputation.compute_reputation(agent1_id)
    
    # Step 2: Get reputation history
    history = reputation.get_reputation_history(agent1_id)
    
    # Verify the history
    assert len(history) == 3
    
    # Verify timestamps are in descending order (newest first)
    timestamps = [score.get_timestamp() for score in history]
    assert timestamps[0] >= timestamps[1] >= timestamps[2] 