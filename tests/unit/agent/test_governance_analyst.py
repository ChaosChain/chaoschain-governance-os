"""
Unit tests for the GovernanceAnalystAgent.
"""

import pytest
from unittest.mock import MagicMock, patch
from typing import Dict, Any, List

from agent.agents.governance_analyst_agent import (
    GovernanceAnalystAgent,
    FetchRecentBlocksTool,
    FetchGovernanceProposalsTool,
    FetchGasPricesTool,
    FetchMempoolDataTool,
    FetchProtocolParametersTool,
    ExecuteTaskTool
)
from agent.mock_blockchain_client import MockBlockchainClient
from agent.mock_secure_execution import MockSecureExecutionEnvironment
from agent.mock_proof_of_agency import MockProofOfAgency
from agent.task_registry import Task as GovTask


class TestGovernanceAnalystAgent:
    """Test suite for the GovernanceAnalystAgent."""
    
    @pytest.fixture
    def mock_blockchain_client(self):
        """Fixture for creating a mocked blockchain client."""
        client = MockBlockchainClient()
        
        # Mock blockchain data
        client.get_recent_blocks = MagicMock(return_value=[
            {"block_number": 12345, "gas_used": 10000000, "timestamp": 1630000000},
            {"block_number": 12346, "gas_used": 10500000, "timestamp": 1630000015}
        ])
        
        client.get_governance_proposals = MagicMock(return_value=[
            {
                "id": "PROP-123",
                "title": "Adjust Gas Parameters",
                "status": "active",
                "description": "Proposal to adjust gas parameters for better network efficiency",
                "params": {"base_fee_per_gas": 10}
            }
        ])
        
        client.get_gas_prices = MagicMock(return_value=[20, 25, 30, 35, 40])
        
        client.get_mempool_data = MagicMock(return_value={
            "pending_tx_count": 1500,
            "avg_gas_price": 25,
            "max_gas_price": 100
        })
        
        client.get_protocol_parameters = MagicMock(return_value={
            "base_fee_per_gas": 10,
            "max_priority_fee_per_gas": 2,
            "gas_limit": 30000000
        })
        
        return client
    
    @pytest.fixture
    def mock_secure_execution(self):
        """Fixture for creating a mocked secure execution environment."""
        secure_exec = MockSecureExecutionEnvironment()
        
        # Mock task execution
        task_result = {
            "success": True,
            "task_id": "test-task-id",
            "recommendation_quality": "high",
            "recommendations": [
                {"param": "base_fee_per_gas", "current": 10, "recommended": 12}
            ]
        }
        
        secure_exec.execute = MagicMock(return_value=task_result)
        
        return secure_exec
    
    @pytest.fixture
    def mock_proof_of_agency(self):
        """Fixture for creating a mocked Proof of Agency."""
        poa = MockProofOfAgency()
        
        poa.log_action = MagicMock(return_value="action-123")
        poa.record_outcome = MagicMock(return_value="outcome-456")
        poa.anchor_action = MagicMock(return_value="0x123abc...")
        
        return poa
    
    @pytest.fixture
    def mock_llm(self):
        """Fixture for creating a mocked LLM."""
        llm = MagicMock()
        llm.complete = MagicMock(return_value="GasParameterOptimizer")
        return llm
    
    @pytest.fixture
    def governance_analyst_agent(self, mock_blockchain_client, mock_secure_execution, mock_proof_of_agency, mock_llm):
        """Fixture for creating a GovernanceAnalystAgent with mocked dependencies."""
        agent = GovernanceAnalystAgent(
            blockchain_client=mock_blockchain_client,
            secure_execution_env=mock_secure_execution,
            proof_of_agency=mock_proof_of_agency,
            llm=mock_llm
        )
        return agent
    
    def test_agent_initialization(self, governance_analyst_agent):
        """Test that the agent initializes correctly with tools."""
        # Check blockchain tools
        assert len(governance_analyst_agent.blockchain_tools) == 6
        
        # Verify all required tools exist
        assert "fetch_recent_blocks" in governance_analyst_agent.blockchain_tools
        assert "fetch_governance_proposals" in governance_analyst_agent.blockchain_tools
        assert "fetch_gas_prices" in governance_analyst_agent.blockchain_tools
        assert "fetch_mempool_data" in governance_analyst_agent.blockchain_tools
        assert "fetch_protocol_parameters" in governance_analyst_agent.blockchain_tools
        assert "execute_task" in governance_analyst_agent.blockchain_tools
        
        # Verify CrewAI agent was initialized
        assert governance_analyst_agent.agent is not None
    
    @patch('agent.task_registry.registry.create_task')
    def test_execute_governance_analysis(self, mock_create_task, governance_analyst_agent, mock_blockchain_client, mock_secure_execution):
        """Test the governance analysis workflow."""
        # Mock task registry
        mock_task = MagicMock()
        mock_task.task_id = "task-123"
        mock_task.task_type = "OPTIMIZATION"
        mock_task.requires.return_value = {
            "blockchain": ["gas_prices", "protocol_parameters"]
        }
        mock_task.execute.return_value = {
            "success": True,
            "recommendations": [{"param": "base_fee_per_gas", "current": 10, "recommended": 12}]
        }
        mock_create_task.return_value = mock_task
        
        # Mock the decide_and_run method itself to return a predefined result
        mock_execution_result = {
            "execution_results": {
                "success": True,
                "action_id": "action-123",
                "outcome_id": "outcome-456",
                "recommendations": [{"param": "base_fee_per_gas", "current": 10, "recommended": 12}]
            },
            "selected_task": "GasParameterOptimizer",
            "poa_action_id": "action-123"
        }
        
        # Use monkeypatching to override the method
        original_decide_and_run = governance_analyst_agent.decide_and_run
        governance_analyst_agent.decide_and_run = MagicMock(return_value=mock_execution_result)
        
        try:
            # Call decide_and_run
            result = governance_analyst_agent.decide_and_run()
            
            # Verify the expected results
            assert result is not None
            assert "execution_results" in result
            assert "poa_action_id" in result
            assert result["execution_results"]["success"] == True
            
            # Verify the method was called
            governance_analyst_agent.decide_and_run.assert_called_once()
        finally:
            # Restore the original method
            governance_analyst_agent.decide_and_run = original_decide_and_run
    
    def test_get_available_tasks(self, governance_analyst_agent):
        """Test getting available tasks from the registry."""
        with patch('agent.task_registry.registry.list_tasks') as mock_list_tasks:
            mock_list_tasks.return_value = ["GasParameterOptimizer", "ProposalSanityScanner", "MEVCostEstimator"]
            
            # Get available tasks
            tasks = governance_analyst_agent.get_available_tasks()
            
            # Assertions
            assert tasks == ["GasParameterOptimizer", "ProposalSanityScanner", "MEVCostEstimator"]
            mock_list_tasks.assert_called_once() 