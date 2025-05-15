"""
Secure Simulation

This module provides a secure simulation environment for evaluating proposal effects
using the ChaosCore Secure Execution Environment.
"""

import uuid
import json
from typing import Dict, Any, Optional, Callable

from simulation.sim_harness import SimulationHarness
from adapters import SecureExecutionAdapter


class SecureSimulation:
    """
    Secure simulation environment for evaluating proposal effects.
    
    This class wraps the SimulationHarness in the ChaosCore Secure Execution Environment,
    providing attestations for simulation results.
    """
    
    def __init__(self, secure_execution_adapter: SecureExecutionAdapter):
        """
        Initialize the secure simulation environment.
        
        Args:
            secure_execution_adapter: Adapter for the secure execution environment
        """
        self._secure_execution = secure_execution_adapter
    
    def simulate_proposal(
        self,
        proposal_data: Dict[str, Any],
        simulation_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Simulate a proposal in the secure execution environment.
        
        Args:
            proposal_data: The proposal data to simulate
            simulation_params: Optional simulation parameters
            
        Returns:
            Dictionary with simulation results and attestation
        """
        # Prepare simulation parameters
        params = simulation_params or {}
        
        # Run the simulation in the secure execution environment
        result = self._secure_execution.execute_proposal_simulation(
            simulation_func=self._run_simulation,
            proposal_data=proposal_data,
            simulation_params=params
        )
        
        return result
    
    def _run_simulation(
        self,
        proposal_data: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Run a simulation of the proposal.
        
        This method is executed in the secure execution environment.
        
        Args:
            proposal_data: The proposal data to simulate
            **kwargs: Additional simulation parameters
            
        Returns:
            Dictionary with simulation results
        """
        # Extract parameters from the proposal and kwargs
        transaction_count = kwargs.get("transaction_count", 100)
        gas_limit = kwargs.get("gas_limit", 12500000)
        base_fee_per_gas = kwargs.get("base_fee_per_gas", 10 * 10**9)
        fee_denominator = kwargs.get("fee_denominator", 5)
        use_predefined_transactions = kwargs.get("use_predefined_transactions", False)
        
        # Extract proposal parameters
        parameters = {}
        proposal_params = proposal_data.get("parameters", {})
        
        if proposal_params:
            parameters = proposal_params
        else:
            # Try to extract parameters from proposal text
            proposal_text = proposal_data.get("proposal", "")
            if isinstance(proposal_text, str):
                # Very simple extraction - in a real system this would be more sophisticated
                if "gas_limit:" in proposal_text or "gas limit:" in proposal_text:
                    try:
                        # Extract gas limit value
                        if "gas_limit:" in proposal_text:
                            gas_limit_text = proposal_text.split("gas_limit:")[1].split("\n")[0].strip()
                        else:
                            gas_limit_text = proposal_text.split("gas limit:")[1].split("\n")[0].strip()
                        extracted_gas_limit = int(gas_limit_text.replace(",", ""))
                        parameters["gas_limit"] = extracted_gas_limit
                        gas_limit = extracted_gas_limit  # Update gas_limit parameter
                    except:
                        pass
                    
                if "base fee max change denominator:" in proposal_text or "base_fee_max_change_denominator:" in proposal_text:
                    try:
                        # Extract denominator value
                        if "base_fee_max_change_denominator:" in proposal_text:
                            key = "base_fee_max_change_denominator:"
                        else:
                            key = "base fee max change denominator:"
                        denominator_text = proposal_text.split(key)[1].split("\n")[0].strip()
                        extracted_denominator = int(denominator_text)
                        parameters["base_fee_max_change_denominator"] = extracted_denominator
                        fee_denominator = extracted_denominator  # Update fee_denominator parameter
                    except:
                        pass
        
        # Create simulation harness
        harness = SimulationHarness(
            transaction_count=transaction_count,
            gas_limit=gas_limit,
            base_fee_per_gas=base_fee_per_gas,
            fee_denominator=fee_denominator,
            use_predefined_transactions=use_predefined_transactions
        )
        
        # Ensure parameters has simulation_blocks
        if "simulation_blocks" not in parameters:
            parameters["simulation_blocks"] = kwargs.get("simulation_blocks", 100)
        
        # Add gas_limit and fee_denominator if not already present
        if "gas_limit" not in parameters:
            parameters["gas_limit"] = gas_limit
        if "base_fee_max_change_denominator" not in parameters:
            parameters["base_fee_max_change_denominator"] = fee_denominator
        
        # Run the simulation
        simulation_result = harness.run_simulation(parameters)
        
        # Add metadata
        simulation_result["metadata"] = {
            "simulation_id": str(uuid.uuid4()),
            "timestamp": kwargs.get("timestamp", str(uuid.uuid4())),
            "proposal_id": proposal_data.get("id", "unknown"),
            "parameters": parameters
        }
        
        return simulation_result 