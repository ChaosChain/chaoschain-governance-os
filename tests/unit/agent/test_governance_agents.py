"""
Test Governance Agents

Tests for the governance agents implementation.
"""

import os
import json
import pytest
from unittest.mock import patch, MagicMock

from agent.agents.governance_agents import GovernanceAgents
from agent.agents.researcher.gas_metrics_researcher import GasMetricsResearcher
from agent.agents.developer.parameter_optimizer import ParameterOptimizer


@pytest.fixture
def mock_task():
    """Create a mock task for testing."""
    task = MagicMock()
    task.description = "Mock task description"
    return task


@pytest.fixture
def mock_agents():
    """Mock agents for testing."""
    with patch("agent.agents.governance_agents.GasMetricsResearcher") as mock_researcher_cls, \
         patch("agent.agents.governance_agents.ParameterOptimizer") as mock_optimizer_cls, \
         patch("agent.agents.governance_agents.Crew") as mock_crew_cls, \
         patch("agent.agents.governance_agents.Task") as mock_task_cls:
        
        # Setup researcher mock
        mock_researcher = MagicMock()
        mock_researcher_agent = MagicMock()
        mock_researcher.get_agent.return_value = mock_researcher_agent
        mock_researcher_cls.return_value = mock_researcher
        
        # Setup optimizer mock
        mock_optimizer = MagicMock()
        mock_optimizer_agent = MagicMock()
        mock_optimizer.get_agent.return_value = mock_optimizer_agent
        mock_optimizer_cls.return_value = mock_optimizer
        
        # Setup Task mocks
        research_task = MagicMock()
        proposal_task = MagicMock()
        mock_task_cls.side_effect = [research_task, proposal_task]
        
        # Setup crew mock
        mock_crew_instance = MagicMock()
        mock_crew_cls.return_value = mock_crew_instance
        
        # Create GovernanceAgents with mocks
        gov_agents = GovernanceAgents()
        
        # Return all mocks for assertions
        return {
            "governance_agents": gov_agents,
            "crew_instance": mock_crew_instance,
            "researcher": mock_researcher,
            "researcher_agent": mock_researcher_agent,
            "optimizer": mock_optimizer,
            "optimizer_agent": mock_optimizer_agent,
            "crew_cls": mock_crew_cls,
            "task_cls": mock_task_cls,
            "research_task": research_task,
            "proposal_task": proposal_task
        }


def test_governance_agents_initialization(mock_agents):
    """Test that the governance agents initialize correctly."""
    # Verify agents were created
    assert mock_agents["researcher"].get_agent.called
    assert mock_agents["optimizer"].get_agent.called
    
    # Verify crew was created with the right agents
    mock_agents["crew_cls"].assert_called_once()
    
    # Verify Task was created
    assert mock_agents["task_cls"].call_count == 2


def test_governance_agents_run(mock_agents):
    """Test that the governance agents run method works correctly."""
    # Setup mock for kickoff method
    mock_agents["crew_instance"].kickoff.return_value = ["analysis result", "proposal result"]
    
    # Run the agents
    result = mock_agents["governance_agents"].run()
    
    # Verify kickoff was called
    mock_agents["crew_instance"].kickoff.assert_called_once()
    
    # Verify result structure
    assert "analysis" in result
    assert "proposal" in result
    assert result["analysis"] == "analysis result"
    assert result["proposal"] == "proposal result"


def test_governance_agents_tasks(mock_agents):
    """Test that the governance agents create the correct tasks."""
    # Check Task constructor calls
    task_calls = mock_agents["task_cls"].call_args_list
    assert len(task_calls) == 2
    
    # Check first task (research)
    research_call_kwargs = task_calls[0][1]
    assert "description" in research_call_kwargs
    assert "agent" in research_call_kwargs
    assert "expected_output" in research_call_kwargs
    assert "analyze" in research_call_kwargs["description"].lower()
    assert "gas metrics" in research_call_kwargs["description"].lower()
    assert mock_agents["researcher_agent"] == research_call_kwargs["agent"]
    
    # Check second task (proposal)
    proposal_call_kwargs = task_calls[1][1]
    assert "description" in proposal_call_kwargs
    assert "agent" in proposal_call_kwargs
    assert "expected_output" in proposal_call_kwargs
    assert "context" in proposal_call_kwargs
    assert "proposal" in proposal_call_kwargs["description"].lower()
    assert "parameter" in proposal_call_kwargs["description"].lower()
    assert mock_agents["optimizer_agent"] == proposal_call_kwargs["agent"]
    
    # Verify the research task is in the context of the proposal task
    assert mock_agents["research_task"] in proposal_call_kwargs["context"] 