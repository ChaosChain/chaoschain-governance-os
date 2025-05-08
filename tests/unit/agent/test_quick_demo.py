"""Unit tests for QuickDemo agent-based governance implementation."""

import pytest
from unittest.mock import MagicMock, patch

from agent.agents.quick_demo import QuickDemo, DemoResearcher, DemoOptimizer


@pytest.fixture
def demo_researcher():
    """Create a DemoResearcher instance."""
    return DemoResearcher()


@pytest.fixture
def demo_optimizer():
    """Create a DemoOptimizer instance."""
    return DemoOptimizer()


def test_demo_researcher_analysis():
    """Test that DemoResearcher provides deterministic analysis."""
    researcher = DemoResearcher()
    analysis = researcher.analyze_gas_metrics()
    
    # Verify the output is a string and contains expected elements
    assert isinstance(analysis, str)
    assert "Gas Metrics Analysis" in analysis
    assert "Executive Summary" in analysis
    assert "Key Metrics" in analysis
    assert "Average gas used ratio" in analysis
    assert "Optimization Opportunities" in analysis


def test_demo_optimizer_proposal():
    """Test that DemoOptimizer creates deterministic proposals."""
    optimizer = DemoOptimizer()
    analysis = "Sample analysis text"
    proposal = optimizer.create_proposal(analysis)
    
    # Verify the output is a string and contains expected elements
    assert isinstance(proposal, str)
    assert "Parameter Optimization Proposal" in proposal
    assert "Proposed Parameters" in proposal
    assert "Gas Limit Adjustment" in proposal
    assert "Expected Benefits" in proposal
    assert "Risks and Mitigations" in proposal


@patch('agent.agents.quick_demo.Crew')
@patch('agent.agents.quick_demo.DemoResearcher')
@patch('agent.agents.quick_demo.DemoOptimizer')
@patch('agent.agents.quick_demo.Task')
def test_quick_demo_initialization(mock_task_cls, mock_optimizer_cls, mock_researcher_cls, mock_crew_cls):
    """Test that QuickDemo initializes correctly with mocked objects."""
    # Setup mock objects
    mock_researcher = MagicMock()
    mock_optimizer = MagicMock()
    mock_researcher_cls.return_value = mock_researcher
    mock_optimizer_cls.return_value = mock_optimizer

    # Create a QuickDemo instance
    QuickDemo()
    
    # Verify that the agents were created
    assert mock_researcher_cls.called
    assert mock_optimizer_cls.called
    assert mock_crew_cls.called


@patch('agent.agents.quick_demo.Crew')
def test_quick_demo_run(mock_crew_cls):
    """Test that QuickDemo's run method returns expected results."""
    # Setup mock crew
    mock_crew_instance = MagicMock()
    mock_crew_instance.kickoff.return_value = ["analysis result", "proposal result"]
    mock_crew_cls.return_value = mock_crew_instance
    
    # Create QuickDemo with appropriate mocks
    with patch('agent.agents.quick_demo.QuickDemo._create_tasks', return_value=[]):
        demo = QuickDemo()
        
        # Run the demo
        result = demo.run()
        
        # Verify the results
        assert "analysis" in result
        assert "proposal" in result
        assert result["analysis"] == "analysis result"
        assert result["proposal"] == "proposal result"


def test_analyze_gas_metrics_tool():
    """Test the analyze_gas_metrics tool function directly."""
    with patch("agent.agents.quick_demo.DemoResearcher") as mock_researcher_cls:
        # Setup mock
        mock_researcher = MagicMock()
        mock_researcher.analyze_gas_metrics.return_value = "Mock analysis"
        mock_researcher_cls.return_value = mock_researcher
        
        # Call the function directly on a mock
        mock_demo = MagicMock()
        QuickDemo._analyze_gas_metrics(mock_demo)
        
        # Verify the correct function was called
        assert mock_researcher_cls.called
        assert mock_researcher.analyze_gas_metrics.called


def test_create_proposal_tool():
    """Test the create_proposal tool function directly."""
    with patch("agent.agents.quick_demo.DemoOptimizer") as mock_optimizer_cls:
        # Setup mock
        mock_optimizer = MagicMock()
        mock_optimizer.create_proposal.return_value = "Mock proposal"
        mock_optimizer_cls.return_value = mock_optimizer
        
        # Call the function directly on a mock
        mock_demo = MagicMock()
        analysis = "Test analysis"
        QuickDemo._create_proposal(mock_demo, analysis)
        
        # Verify the correct function was called
        assert mock_optimizer_cls.called
        assert mock_optimizer.create_proposal.called
        mock_optimizer.create_proposal.assert_called_with(analysis) 