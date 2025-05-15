"""
Integration tests for secure simulation with proof of agency.
"""

import unittest
import json
from typing import Dict, Any

from chaoscore.core.agent_registry import InMemoryAgentRegistry
from chaoscore.core.proof_of_agency import InMemoryProofOfAgency
from chaoscore.core.secure_execution import InMemorySecureExecution

from adapters import AgentRegistryAdapter, ProofOfAgencyAdapter, SecureExecutionAdapter
from simulation.secure_simulation import SecureSimulation


class TestSecureSimulationWithProofOfAgency(unittest.TestCase):
    """Integration tests for secure simulation with proof of agency."""
    
    def setUp(self):
        """Set up the test environment."""
        # Create core components
        self.agent_registry = InMemoryAgentRegistry()
        self.proof_of_agency = InMemoryProofOfAgency()
        self.secure_execution = InMemorySecureExecution()
        
        # Create adapters
        self.agent_registry_adapter = AgentRegistryAdapter(self.agent_registry)
        self.proof_of_agency_adapter = ProofOfAgencyAdapter(self.proof_of_agency)
        self.secure_execution_adapter = SecureExecutionAdapter(self.secure_execution)
        
        # Create secure simulation
        self.secure_simulation = SecureSimulation(self.secure_execution_adapter)
        
        # Register test agents
        self.agent_data = {
            "researcher": {
                "email": "researcher@chaoscore.io",
                "name": "Test Researcher",
            },
            "developer": {
                "email": "developer@chaoscore.io",
                "name": "Test Developer",
            }
        }
        self.agent_ids = self.agent_registry_adapter.register_governance_agents(self.agent_data)
    
    def test_end_to_end_simulation_with_poa(self):
        """Test an end-to-end simulation flow with proof of agency."""
        # Create a test proposal
        proposal_data = {
            "id": "test-proposal-1",
            "title": "Test Gas Parameter Optimization",
            "proposal": """
            Based on the gas metrics analysis, I propose the following parameter changes:
            
            gas_limit: 20000000
            base_fee_max_change_denominator: 10
            
            These changes will improve network efficiency by reducing congestion.
            """
        }
        
        # Log the proposal creation action
        proposal_action_id = self.proof_of_agency_adapter.log_action(
            agent_id=self.agent_ids["developer"],
            action_type="CREATE",
            description="Generate parameter optimization proposal",
            data={"proposal_id": proposal_data["id"]}
        )
        
        # Run the secure simulation
        simulation_result = self.secure_simulation.simulate_proposal(proposal_data)
        
        # Record the simulation outcome
        self.proof_of_agency_adapter.record_outcome(
            action_id=proposal_action_id,
            success=True,
            results={
                "simulation": simulation_result["result"],
                "attestation_hash": simulation_result["attestation"]["hash"]
            },
            impact_score=0.9
        )
        
        # Verify the simulation action
        self.proof_of_agency_adapter.verify_action(
            action_id=proposal_action_id,
            verifier_id=self.agent_ids["researcher"],
            verification_data={"attestation_hash": simulation_result["attestation"]["hash"]}
        )
        
        # Checks
        
        # 1. Verify that the simulation result contains the expected data
        self.assertIn("result", simulation_result)
        
        # Get the action record
        action = self.proof_of_agency.get_action(proposal_action_id)
        
        # 2. Verify that the action was recorded
        self.assertIsNotNone(action)
        
        # 3. Verify that the outcome was recorded
        self.assertIsNotNone(action.outcome)
        
        # 4. Verify that the action was verified
        self.assertTrue(action.is_verified)
        
        # 5. Verify that the attestation hash is recorded in the outcome
        self.assertIn("attestation_hash", action.outcome.results)
        
        # 6. Verify that the simulation result contains the correct parameters
        results = simulation_result["result"]
        self.assertIn("simulation_config", results)
        self.assertIn("parameters", results["simulation_config"])
        
        parameters = results["simulation_config"]["parameters"]
        self.assertEqual(parameters.get("gas_limit"), 20000000)
        self.assertEqual(parameters.get("base_fee_max_change_denominator"), 10)
    
    def test_simulation_extraction_from_text(self):
        """Test that parameters are correctly extracted from proposal text."""
        # Create a test proposal with text format
        proposal_data = {
            "id": "test-proposal-2",
            "title": "Test Parameter Extraction",
            "proposal": """
            I propose changing the following parameters:
            
            gas limit: 18000000
            base fee max change denominator: 12
            
            These values should optimize for current network conditions.
            """
        }
        
        # Run the secure simulation
        simulation_result = self.secure_simulation.simulate_proposal(proposal_data)
        
        # Extract the parameters from the result
        results = simulation_result["result"]
        parameters = results["simulation_config"]["parameters"]
        
        # Verify the parameters were correctly extracted
        self.assertEqual(parameters.get("gas_limit"), 18000000)
        self.assertEqual(parameters.get("base_fee_max_change_denominator"), 12)
    
    def test_simulation_with_structured_parameters(self):
        """Test simulation with structured parameters."""
        # Create a test proposal with structured parameters
        proposal_data = {
            "id": "test-proposal-3",
            "title": "Test Structured Parameters",
            "parameters": {
                "gas_limit": 25000000,
                "base_fee_max_change_denominator": 6,
                "simulation_blocks": 200
            }
        }
        
        # Run the secure simulation
        simulation_result = self.secure_simulation.simulate_proposal(proposal_data)
        
        # Extract the parameters from the result
        results = simulation_result["result"]
        parameters = results["simulation_config"]["parameters"]
        
        # Verify the parameters were correctly used
        self.assertEqual(parameters.get("gas_limit"), 25000000)
        self.assertEqual(parameters.get("base_fee_max_change_denominator"), 6)
        self.assertEqual(parameters.get("simulation_blocks"), 200)


if __name__ == '__main__':
    unittest.main() 