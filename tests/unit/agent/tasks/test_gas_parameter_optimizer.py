"""
Unit tests for the GasParameterOptimizer task.
"""

import unittest
from unittest.mock import patch, MagicMock
import logging
import random
from typing import Dict, List, Any

from agent.tasks.gas_parameter_optimizer import GasParameterOptimizer

# Suppress logging during tests
logging.disable(logging.CRITICAL)

class TestGasParameterOptimizer(unittest.TestCase):
    """Unit tests for the GasParameterOptimizer task."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.task = GasParameterOptimizer()
        self.test_context = self._create_test_context()
    
    def _create_test_context(self) -> Dict[str, Any]:
        """Create a test context with mock blockchain data."""
        # Create mock blocks
        blocks = []
        for i in range(200):
            gas_used = random.randint(10000000, 15000000)
            blocks.append({
                "number": 1000000 + i,
                "gasUsed": gas_used,
                "gasLimit": 15000000
            })
        
        # Create mock gas prices
        gas_prices = [random.randint(20, 50) for _ in range(200)]
        
        # Create mock transaction history
        tx_history = [
            {"gas_used": random.randint(100000, 500000), "gas_price": random.randint(20, 50)}
            for _ in range(100)
        ]
        
        # Create mock proposal types
        proposal_types = ["standard", "complex", "upgrade"]
        
        # Create mock context
        return {
            "blockchain": {
                "recent_blocks": blocks,
                "gas_prices": gas_prices,
                "transaction_history": tx_history
            },
            "governance": {
                "proposal_types": proposal_types,
                "voting_contract_address": "0x1234567890123456789012345678901234567890"
            },
            "context": {
                "network_congestion": 0.5,
                "timestamp": 1234567890,
                "network": "ethereum",
                "proposal_type": "standard"
            }
        }
    
    def test_initialize(self):
        """Test initialization with default parameters."""
        self.assertIsNotNone(self.task)
        self.assertEqual(self.task.task_type, "gas_optimization")
        self.assertIn("sample_size", self.task.parameters)
        self.assertIn("percentile_base", self.task.parameters)
        self.assertIn("volatility_factor", self.task.parameters)
    
    def test_requires(self):
        """Test that the required data is correctly specified."""
        required = self.task.requires()
        self.assertIn("blockchain", required)
        self.assertIn("governance", required)
        self.assertIn("context", required)
        
        self.assertIn("recent_blocks", required["blockchain"])
        self.assertIn("gas_prices", required["blockchain"])
        self.assertIn("transaction_history", required["blockchain"])
        
        self.assertIn("proposal_types", required["governance"])
        self.assertIn("voting_contract_address", required["governance"])
        
        self.assertIn("network_congestion", required["context"])
    
    def test_execute_success(self):
        """Test successful execution with mock data."""
        result = self.task.execute(self.test_context)
        
        self.assertTrue(result["success"])
        self.assertIn("recommendations", result)
        self.assertIn("metadata", result)
        
        recommendations = result["recommendations"]
        self.assertIn("gas_price", recommendations)
        self.assertIn("gas_limit", recommendations)
        self.assertIn("estimated_cost_eth", recommendations)
        self.assertIn("priority_fee", recommendations)
        self.assertIn("recommendation_quality", recommendations)
    
    def test_execute_missing_data(self):
        """Test execution with missing required data."""
        # Create a context with missing blocks
        context_missing_blocks = {
            "blockchain": {
                "gas_prices": self.test_context["blockchain"]["gas_prices"],
                "transaction_history": self.test_context["blockchain"]["transaction_history"]
            },
            "governance": self.test_context["governance"],
            "context": self.test_context["context"]
        }
        
        result = self.task.execute(context_missing_blocks)
        self.assertFalse(result["success"])
        self.assertIn("error", result)
        
        # Create a context with missing gas prices
        context_missing_gas = {
            "blockchain": {
                "recent_blocks": self.test_context["blockchain"]["recent_blocks"],
                "transaction_history": self.test_context["blockchain"]["transaction_history"]
            },
            "governance": self.test_context["governance"],
            "context": self.test_context["context"]
        }
        
        result = self.task.execute(context_missing_gas)
        self.assertFalse(result["success"])
        self.assertIn("error", result)
    
    def test_calculate_recommendations(self):
        """Test the recommendation calculation logic."""
        # Extract method for testing
        result = self.task._calculate_recommendations(
            self.test_context["blockchain"]["recent_blocks"],
            self.test_context["blockchain"]["gas_prices"],
            self.test_context["context"]
        )
        
        # Check recommendation structure
        self.assertIn("gas_price", result)
        self.assertIn("recommended", result["gas_price"])
        self.assertIn("max", result["gas_price"])
        self.assertIn("unit", result["gas_price"])
        self.assertEqual(result["gas_price"]["unit"], "gwei")
        
        self.assertIn("gas_limit", result)
        self.assertGreater(result["gas_limit"], 0)
        
        self.assertIn("estimated_cost_eth", result)
        self.assertGreater(result["estimated_cost_eth"], 0)
        
        self.assertIn("priority_fee", result)
        self.assertGreater(result["priority_fee"], 0)
        
        # Check recommendation quality
        self.assertIn("recommendation_quality", result)
        self.assertIn(result["recommendation_quality"], ["high", "medium", "low"])
    
    def test_calculate_recommendation_quality(self):
        """Test the recommendation quality calculation."""
        # Test high quality case
        gas_used = [12000000] * 100  # Low variance
        gas_prices = [30] * 100  # Low variance
        
        quality = self.task._calculate_recommendation_quality(gas_used, gas_prices)
        self.assertEqual(quality, "high")
        
        # Test medium quality case
        gas_used = [random.randint(10000000, 14000000) for _ in range(100)]  # Medium variance
        gas_prices = [random.randint(25, 35) for _ in range(100)]  # Medium variance
        
        quality = self.task._calculate_recommendation_quality(gas_used, gas_prices)
        self.assertIn(quality, ["medium", "low"])  # Could be either depending on random values
        
        # Test low quality case (empty data)
        quality = self.task._calculate_recommendation_quality([], [])
        self.assertEqual(quality, "low")
    
    def test_parameters_effect(self):
        """Test how parameter changes affect the recommendations."""
        # Save original parameters
        original_params = self.task.parameters.copy()
        
        try:
            # Test with higher percentile base
            self.task.parameters["percentile_base"] = 90
            result_high_percentile = self.task._calculate_recommendations(
                self.test_context["blockchain"]["recent_blocks"],
                self.test_context["blockchain"]["gas_prices"],
                self.test_context["context"]
            )
            
            # Reset parameters
            self.task.parameters = original_params.copy()
            
            # Test with lower percentile base
            self.task.parameters["percentile_base"] = 50
            result_low_percentile = self.task._calculate_recommendations(
                self.test_context["blockchain"]["recent_blocks"],
                self.test_context["blockchain"]["gas_prices"],
                self.test_context["context"]
            )
            
            # Higher percentile should recommend higher gas price
            self.assertGreaterEqual(
                result_high_percentile["gas_price"]["recommended"],
                result_low_percentile["gas_price"]["recommended"]
            )
            
        finally:
            # Restore original parameters
            self.task.parameters = original_params

if __name__ == '__main__':
    unittest.main() 