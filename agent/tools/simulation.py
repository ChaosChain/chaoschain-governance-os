"""
Simulation Tools

This module provides tools for simulating blockchain parameter changes
and evaluating their effects.
"""

import os
import json
import subprocess
from typing import Dict, Any, List
from langchain.tools import BaseTool
import tempfile

class SimulationTool(BaseTool):
    """Tool for simulating parameter changes and evaluating outcomes."""
    
    name: str = "parameter_simulator"
    description: str = """
    Simulate the effects of changing blockchain parameters.
    Provide a dictionary with proposed parameter changes and receive simulation results.
    The simulation predicts network behavior under the new parameters.
    
    Parameters should be a JSON string with the following format:
    {
        "parameter_name": new_value,
        "simulation_blocks": number_of_blocks_to_simulate
    }
    
    For example:
    {
        "gas_limit": 30000000,
        "base_fee_max_change_denominator": 8,
        "simulation_blocks": 100
    }
    """
    
    def _run(self, parameters_json: str) -> str:
        """
        Simulate parameter changes and evaluate their effects.
        
        Args:
            parameters_json: JSON string with parameter changes
            
        Returns:
            JSON string with simulation results
        """
        try:
            parameters = json.loads(parameters_json)
            
            # Validate parameters
            if not isinstance(parameters, dict):
                return json.dumps({"error": "Parameters must be a JSON object"})
            
            # Extract simulation blocks
            simulation_blocks = parameters.pop("simulation_blocks", 100)
            if not isinstance(simulation_blocks, int) or simulation_blocks <= 0:
                return json.dumps({"error": "simulation_blocks must be a positive integer"})
                
            # In a real implementation, this would call out to a proper simulation environment
            # For now, we'll provide a mock implementation that returns realistic-looking results
            simulation_results = self._mock_simulation(parameters, simulation_blocks)
            
            return json.dumps(simulation_results, indent=2)
        except json.JSONDecodeError:
            return json.dumps({"error": "Invalid JSON format for parameters"})
        except Exception as e:
            return json.dumps({"error": str(e)})
    
    def _mock_simulation(self, parameters: Dict[str, Any], simulation_blocks: int) -> Dict[str, Any]:
        """
        Produce mock simulation results for parameter changes.
        
        Args:
            parameters: Dictionary of parameter changes
            simulation_blocks: Number of blocks to simulate
            
        Returns:
            Dictionary with simulation results
        """
        results = {
            "simulation_config": {
                "blocks_simulated": simulation_blocks,
                "parameters": parameters
            },
            "baseline": {},
            "modified": {},
            "comparison": {},
            "analysis": {
                "findings": [],
                "recommendations": []
            }
        }
        
        # Generate mock baseline metrics
        results["baseline"] = {
            "avg_gas_used_ratio": 0.55,
            "avg_base_fee_gwei": 25.0,
            "fee_volatility": 0.3,
            "tx_inclusion_rate": 0.95,
            "avg_block_time_seconds": 12.1
        }
        
        # Generate modified metrics based on parameter changes
        modified = results["baseline"].copy()
        
        # Simple logic to adjust metrics based on parameter changes
        if "gas_limit" in parameters:
            current_gas_limit = 15000000  # Example current value
            gas_limit_change_ratio = parameters["gas_limit"] / current_gas_limit
            
            # Reduce gas used ratio if increasing gas limit
            if gas_limit_change_ratio > 1:
                modified["avg_gas_used_ratio"] /= (gas_limit_change_ratio ** 0.5)
                modified["tx_inclusion_rate"] = min(0.99, modified["tx_inclusion_rate"] * 1.05)
            else:
                modified["avg_gas_used_ratio"] *= (1 / gas_limit_change_ratio) ** 0.5
                modified["tx_inclusion_rate"] = max(0.8, modified["tx_inclusion_rate"] * 0.95)
        
        if "base_fee_max_change_denominator" in parameters:
            current_denominator = 8  # EIP-1559 default
            if parameters["base_fee_max_change_denominator"] > current_denominator:
                # Higher denominator = smaller max change
                modified["fee_volatility"] *= (current_denominator / parameters["base_fee_max_change_denominator"])
            else:
                # Lower denominator = larger max change
                modified["fee_volatility"] *= (current_denominator / parameters["base_fee_max_change_denominator"])
        
        results["modified"] = modified
        
        # Generate comparison metrics
        results["comparison"] = {
            key: {
                "absolute_change": modified[key] - results["baseline"][key],
                "percent_change": (modified[key] - results["baseline"][key]) / results["baseline"][key] * 100
            }
            for key in results["baseline"]
        }
        
        # Generate analysis
        if "gas_limit" in parameters:
            if modified["avg_gas_used_ratio"] < 0.3:
                results["analysis"]["findings"].append("Gas usage ratio is very low, suggesting wasted block space")
                results["analysis"]["recommendations"].append("Consider a smaller gas limit increase or no increase")
            elif modified["avg_gas_used_ratio"] > 0.8:
                results["analysis"]["findings"].append("Gas usage ratio remains high, suggesting continued congestion")
                results["analysis"]["recommendations"].append("Consider a larger gas limit increase")
        
        if "base_fee_max_change_denominator" in parameters:
            if modified["fee_volatility"] < 0.15:
                results["analysis"]["findings"].append("Fee volatility is very low, potentially reducing market efficiency")
            elif modified["fee_volatility"] > 0.4:
                results["analysis"]["findings"].append("Fee volatility is high, potentially causing poor user experience")
        
        # Overall recommendation
        if results["comparison"]["tx_inclusion_rate"]["percent_change"] > 5:
            results["analysis"]["findings"].append(f"Transaction inclusion rate improved by {results['comparison']['tx_inclusion_rate']['percent_change']:.1f}%")
            results["analysis"]["recommendations"].append("Parameter changes show positive effects on network performance")
        elif results["comparison"]["tx_inclusion_rate"]["percent_change"] < -5:
            results["analysis"]["findings"].append(f"Transaction inclusion rate decreased by {abs(results['comparison']['tx_inclusion_rate']['percent_change']):.1f}%")
            results["analysis"]["recommendations"].append("Parameter changes may negatively impact network performance")
        
        return results 