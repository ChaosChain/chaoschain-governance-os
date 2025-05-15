"""
Unit tests for the adapted governance agents.
"""

import unittest
from unittest.mock import MagicMock, patch
import uuid

from agent.agents.governance_agents_adapted import AdaptedGovernanceAgents


class TestAdaptedGovernanceAgents(unittest.TestCase):
    """Tests for the AdaptedGovernanceAgents class."""
    
    def setUp(self):
        """Set up mock adapters for each test."""
        # Create mock adapters
        self.agent_registry_adapter = MagicMock()
        self.proof_of_agency_adapter = MagicMock()
        self.secure_execution_adapter = MagicMock()
        self.reputation_adapter = MagicMock()
        self.studio_adapter = MagicMock()
        
        # Configure mock returns
        self.agent_registry_adapter.register_governance_agents.return_value = {
            "researcher": str(uuid.uuid4()),
            "developer": str(uuid.uuid4())
        }
        
        self.proof_of_agency_adapter.log_action.side_effect = [
            str(uuid.uuid4()),  # First call for research action
            str(uuid.uuid4())   # Second call for proposal action
        ]
        
        self.secure_execution_adapter.run.return_value = {
            "result": {"simulation_result": "success"},
            "attestation": {
                "hash": str(uuid.uuid4()),
                "data": {"timestamp": "2023-01-01T00:00:00Z"}
            }
        }
        
        self.reputation_adapter.update_agent_reputation_after_action.return_value = {
            "old_score": 0.5,
            "new_score": 0.7,
            "delta": 0.2
        }
        
        # Mock CrewAI components
        self.mock_crew_result = ["Analysis result", "Proposal result"]
        
        # Create the governance agents with mocked dependencies
        with patch("crewai.Crew") as mock_crew, \
             patch("agent.agents.researcher.gas_metrics_researcher.GasMetricsResearcher") as mock_researcher, \
             patch("agent.agents.developer.parameter_optimizer.ParameterOptimizer") as mock_developer:
            
            # Configure mocks
            mock_crew_instance = mock_crew.return_value
            mock_crew_instance.kickoff.return_value = self.mock_crew_result
            
            mock_researcher_instance = mock_researcher.return_value
            mock_researcher_instance.get_agent.return_value = MagicMock()
            
            mock_developer_instance = mock_developer.return_value
            mock_developer_instance.get_agent.return_value = MagicMock()
            
            # Create the class under test
            self.governance_agents = AdaptedGovernanceAgents(
                agent_registry_adapter=self.agent_registry_adapter,
                proof_of_agency_adapter=self.proof_of_agency_adapter,
                secure_execution_adapter=self.secure_execution_adapter,
                reputation_adapter=self.reputation_adapter,
                studio_adapter=self.studio_adapter
            )
    
    def test_register_agents(self):
        """Test that agents are registered during initialization."""
        # Verify the agent registry adapter was called to register agents
        self.agent_registry_adapter.register_governance_agents.assert_called_once()
        self.assertTrue(hasattr(self.governance_agents, 'agent_ids'))
        self.assertEqual(
            self.governance_agents.agent_ids,
            self.agent_registry_adapter.register_governance_agents.return_value
        )
    
    def test_run_workflow(self):
        """Test running the governance workflow."""
        # Run the workflow
        result = self.governance_agents.run()
        
        # Verify logging of research action
        self.proof_of_agency_adapter.log_action.assert_called()
        
        # Verify crew was run
        self.assertEqual(result["analysis"], self.mock_crew_result[0])
        self.assertEqual(result["proposal"], self.mock_crew_result[1])
        
        # Verify secure execution was used
        self.secure_execution_adapter.run.assert_called_once()
        
        # Verify outcomes were recorded
        self.proof_of_agency_adapter.record_outcome.assert_called()
        
        # Verify actions were verified
        self.proof_of_agency_adapter.verify_action.assert_called()
        
        # Verify actions were anchored
        self.proof_of_agency_adapter.anchor_action.assert_called()
        
        # Verify reputation was updated
        self.reputation_adapter.update_agent_reputation_after_action.assert_called()
        
        # Verify the attestation hash is in the result
        self.assertIn("attestation", result)
        self.assertIn("hash", result["attestation"])
        self.assertEqual(
            result["attestation"]["hash"],
            self.secure_execution_adapter.run.return_value["attestation"]["hash"]
        )
    
    @patch("simulation.sim_harness.SimulationHarness")
    def test_simulate_proposal(self, mock_harness_class):
        """Test the proposal simulation method."""
        # Configure mock
        mock_harness_instance = mock_harness_class.return_value
        mock_harness_instance.run_simulation.return_value = {
            "simulation_result": "success"
        }
        
        # Run the simulation
        proposal_data = {"proposal": "gas_limit: 15000000\nbase_fee_max_change_denominator: 8"}
        result = self.governance_agents._simulate_proposal(proposal_data)
        
        # Verify the harness was created with the correct parameters
        mock_harness_class.assert_called_once()
        
        # Verify the simulation was run
        mock_harness_instance.run_simulation.assert_called_once()
        
        # Verify the result is returned
        self.assertEqual(result, mock_harness_instance.run_simulation.return_value)


if __name__ == '__main__':
    unittest.main() 