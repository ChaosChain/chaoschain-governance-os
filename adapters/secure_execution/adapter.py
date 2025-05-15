"""
Secure Execution Adapter Implementation

This module implements the adapter for connecting the governance system to the ChaosCore
Secure Execution Environment.
"""
import functools
from typing import Dict, Any, Optional, Callable, TypeVar, List
import json

from chaoscore.core.secure_execution import (
    SecureExecutionEnvironment,
    Attestation,
    ExecutionResult
)

# Define type variables for generic functions
T = TypeVar('T')
R = TypeVar('R')


class SecureExecutionAdapter:
    """
    Adapter for the ChaosCore Secure Execution Environment.
    
    This adapter provides methods for executing code in a secure environment
    and generating attestations.
    """
    
    def __init__(self, secure_execution: SecureExecutionEnvironment):
        """
        Initialize the secure execution adapter.
        
        Args:
            secure_execution: ChaosCore Secure Execution Environment implementation
        """
        self._secure_execution = secure_execution
    
    def run(self, func: Callable[..., R], *args, **kwargs) -> Dict[str, Any]:
        """
        Run a function in the secure execution environment.
        
        Args:
            func: Function to execute
            *args: Positional arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function
            
        Returns:
            Dict[str, Any]: Execution result with attestation
        """
        # Execute the function in the secure environment
        execution_result = self._secure_execution.run(func, *args, **kwargs)
        
        # Extract result and attestation
        result = execution_result.get_result()
        attestation = execution_result.get_attestation()
        
        return {
            "result": result,
            "attestation": {
                "hash": attestation.get_hash(),
                "data": attestation.get_data(),
                "timestamp": attestation.get_timestamp().isoformat(),
                "environment": attestation.get_environment_info()
            }
        }
    
    def verify_attestation(self, attestation_hash: str) -> bool:
        """
        Verify an attestation by its hash.
        
        Args:
            attestation_hash: Hash of the attestation to verify
            
        Returns:
            bool: True if attestation is valid
        """
        return self._secure_execution.verify_attestation(attestation_hash)
    
    def execute_proposal_simulation(
        self,
        simulation_func: Callable,
        proposal_data: Dict[str, Any],
        simulation_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a proposal simulation in the secure execution environment.
        
        This is a convenience method specifically for governance proposal simulations.
        
        Args:
            simulation_func: Simulation function to execute
            proposal_data: Proposal data to simulate
            simulation_params: Additional simulation parameters
            
        Returns:
            Dict[str, Any]: Simulation result with attestation
        """
        # Execute the simulation in the secure environment
        result = self.run(
            simulation_func,
            proposal_data=proposal_data,
            **simulation_params
        )
        
        # Add additional metadata
        result["proposal_id"] = proposal_data.get("id", "unknown")
        result["simulation_type"] = "proposal_validation"
        
        return result
    
    def get_attestation_data(self, attestation_hash: str) -> Optional[Dict[str, Any]]:
        """
        Get attestation data by hash.
        
        Args:
            attestation_hash: Hash of the attestation
            
        Returns:
            Dict[str, Any]: Attestation data if found, None otherwise
        """
        attestation = self._secure_execution.get_attestation(attestation_hash)
        if attestation:
            return {
                "hash": attestation.get_hash(),
                "data": attestation.get_data(),
                "timestamp": attestation.get_timestamp().isoformat(),
                "environment": attestation.get_environment_info()
            }
        return None 