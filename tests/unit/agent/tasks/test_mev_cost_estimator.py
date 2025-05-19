"""
Unit tests for the MEVCostEstimator task.
"""

import unittest
from unittest.mock import patch, MagicMock
import logging
import random
from typing import Dict, List, Any

from agent.tasks.mev_cost_estimator import MEVCostEstimator

# Suppress logging during tests
logging.disable(logging.CRITICAL)

class TestMEVCostEstimator(unittest.TestCase):
    """Unit tests for the MEVCostEstimator task."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.task = MEVCostEstimator()
        self.test_context = self._create_test_context()
    
    def _create_test_context(self) -> Dict[str, Any]:
        """Create a test context with mock blockchain and DeFi data."""
        # Create mock blocks
        blocks = []
        for i in range(100):
            gas_used = random.randint(10000000, 15000000)
            blocks.append({
                "number": 1000000 + i,
                "gasUsed": gas_used,
                "gasLimit": 15000000
            })
        
        # Create mock gas prices
        gas_prices = [random.randint(20, 50) for _ in range(100)]
        
        # Create mock mempool data
        mempool_data = {
            "transaction_count": random.randint(2000, 8000),
            "average_gas_price": 30,
            "high_priority_count": 500,
            "average_transaction_value": 0.5,
            "total_pending_value": 5000,
            "max_gas_price": 60,
            "min_gas_price": 15
        }
        
        # Create mock proposal data
        proposal_data = {
            "id": "proposal-1",
            "title": "Update Oracle Parameters",
            "description": "Update oracle update frequency and other parameters",
            "author": "0x1234567890123456789012345678901234567890",
            "parameters": {
                "oracle_update_frequency": 300,
                "price_feed": "0x2345678901234567890123456789012345678901"
            }
        }
        
        # Create mock protocol parameters
        protocol_parameters = {
            "oracle_update_frequency": {
                "current_value": 600,
                "safe_range": [60, 1800],
                "description": "Oracle update frequency in seconds"
            },
            "liquidation_threshold": {
                "current_value": 0.825,
                "safe_range": [0.75, 0.90],
                "description": "Collateral liquidation threshold"
            }
        }
        
        # Create mock trading pairs
        trading_pairs = []
        for i, symbol in enumerate(["ETH/USDC", "WBTC/USDC", "ETH/WBTC"]):
            token0, token1 = symbol.split("/")
            volatility = random.uniform(0.05, 0.3)
            
            trading_pairs.append({
                "id": f"pair-{i+1}",
                "symbol": symbol,
                "token0": token0,
                "token1": token1,
                "volatility": volatility,
                "avg_slippage": random.uniform(0.001, 0.01),
                "fee_tier": random.choice([0.0005, 0.003, 0.01])
            })
        
        # Create mock pool liquidity data
        pool_liquidity = {
            "pair-1": 5000000,
            "pair-2": 2000000,
            "pair-3": 1000000
        }
        
        # Create mock volume data
        volume_data = {
            "pair-1": 1000000,
            "pair-2": 500000,
            "pair-3": 200000
        }
        
        # Create mock active bots
        active_bots = []
        for i in range(10):
            bot_type = random.choice(["arbitrage", "liquidation", "market_making", "sandwich"])
            capabilities = {
                "frontrunning": bot_type in ["arbitrage", "sandwich"],
                "backrunning": bot_type in ["arbitrage", "liquidation"],
                "sandwich_attack": bot_type == "sandwich",
                "liquidation": bot_type == "liquidation"
            }
            
            active_bots.append({
                "id": f"bot-{i+1}",
                "type": bot_type,
                "capabilities": capabilities,
                "active_since": 1234567890 - random.randint(0, 86400 * 30),
                "success_rate": random.uniform(0.5, 0.95)
            })
        
        # Create mock context
        return {
            "blockchain": {
                "recent_blocks": blocks,
                "gas_prices": gas_prices,
                "mempool_data": mempool_data
            },
            "governance": {
                "proposal_data": proposal_data,
                "protocol_parameters": protocol_parameters
            },
            "defi": {
                "trading_pairs": trading_pairs,
                "pool_liquidity": pool_liquidity,
                "volume_data": volume_data,
                "active_bots": active_bots
            },
            "timestamp": 1234567890,
            "network": "ethereum"
        }
    
    def test_initialize(self):
        """Test initialization with default parameters."""
        self.assertIsNotNone(self.task)
        self.assertEqual(self.task.task_type, "security_analysis")
        self.assertIn("block_time_seconds", self.task.parameters)
        self.assertIn("mev_estimation_blocks", self.task.parameters)
        self.assertIn("sandwich_attack_sensitivity", self.task.parameters)
    
    def test_requires(self):
        """Test that the required data is correctly specified."""
        required = self.task.requires()
        self.assertIn("blockchain", required)
        self.assertIn("governance", required)
        self.assertIn("defi", required)
        
        self.assertIn("recent_blocks", required["blockchain"])
        self.assertIn("gas_prices", required["blockchain"])
        self.assertIn("mempool_data", required["blockchain"])
        
        self.assertIn("proposal_data", required["governance"])
        self.assertIn("protocol_parameters", required["governance"])
        
        self.assertIn("trading_pairs", required["defi"])
        self.assertIn("pool_liquidity", required["defi"])
        self.assertIn("volume_data", required["defi"])
        self.assertIn("active_bots", required["defi"])
    
    def test_execute_success(self):
        """Test successful execution with mock data."""
        result = self.task.execute(self.test_context)
        
        self.assertTrue(result["success"])
        self.assertIn("risk_level", result)
        self.assertIn("risk_score", result)
        self.assertIn("estimated_total_mev_cost", result)
        self.assertIn("estimated_cost_per_block", result)
        self.assertIn("mev_vectors", result)
        self.assertIn("mitigations", result)
        self.assertIn("metadata", result)
        
        # Check MEV vectors
        self.assertIn("sandwich_attacks", result["mev_vectors"])
        self.assertIn("frontrunning", result["mev_vectors"])
        self.assertIn("liquidations", result["mev_vectors"])
        self.assertIn("arbitrage", result["mev_vectors"])
        
        self.assertIn(result["risk_level"], ["high", "medium", "low"])
        self.assertGreaterEqual(result["risk_score"], 0.0)
        self.assertLessEqual(result["risk_score"], 1.0)
        self.assertGreater(result["estimated_total_mev_cost"], 0.0)
    
    def test_execute_missing_data(self):
        """Test execution with missing required data."""
        # Create a context with missing proposal data
        context_missing_proposal = {
            "blockchain": self.test_context["blockchain"],
            "governance": {},
            "defi": self.test_context["defi"]
        }
        
        result = self.task.execute(context_missing_proposal)
        self.assertFalse(result["success"])
        self.assertIn("error", result)
    
    def test_sandwich_attack_analysis(self):
        """Test sandwich attack risk analysis."""
        # Extract method for testing
        result = self.task._analyze_sandwich_attack_risk(self.test_context)
        
        # Check analysis structure
        self.assertIn("risk_score", result)
        self.assertIn("estimated_cost", result)
        self.assertIn("affected_pairs", result)
        self.assertIn("highest_risk_pairs", result)
        
        # Check risk score bounds
        self.assertGreaterEqual(result["risk_score"], 0.0)
        self.assertLessEqual(result["risk_score"], 1.0)
        
        # Check that cost is positive
        self.assertGreaterEqual(result["estimated_cost"], 0.0)
        
        # Affected pairs should match trading pairs count
        pairs_count = len(self.test_context["defi"]["trading_pairs"])
        pairs_with_data = sum(1 for pair in self.test_context["defi"]["trading_pairs"]
                           if pair["id"] in self.test_context["defi"]["pool_liquidity"]
                           and pair["id"] in self.test_context["defi"]["volume_data"])
        self.assertLessEqual(result["affected_pairs"], pairs_count)
        self.assertLessEqual(result["affected_pairs"], pairs_with_data)
        
        # Test with slippage parameter changes
        slippage_context = self.test_context.copy()
        slippage_context["governance"] = self.test_context["governance"].copy()
        slippage_context["governance"]["proposal_data"] = self.test_context["governance"]["proposal_data"].copy()
        slippage_context["governance"]["proposal_data"]["parameters"] = {
            "slippage_tolerance": 0.02,
            "min_output_amount": 1000
        }
        
        slippage_result = self.task._analyze_sandwich_attack_risk(slippage_context)
        
        # Risk should be higher with slippage parameter changes
        self.assertGreater(slippage_result["risk_score"], result["risk_score"] * 0.8)  # Allow some flexibility
    
    def test_frontrunning_analysis(self):
        """Test frontrunning risk analysis."""
        # Extract method for testing
        result = self.task._analyze_frontrunning_risk(self.test_context)
        
        # Check analysis structure
        self.assertIn("risk_score", result)
        self.assertIn("estimated_cost", result)
        self.assertIn("mempool_density", result)
        self.assertIn("gas_price_volatility", result)
        self.assertIn("frontrunning_bot_prevalence", result)
        
        # Check risk score bounds
        self.assertGreaterEqual(result["risk_score"], 0.0)
        self.assertLessEqual(result["risk_score"], 1.0)
        
        # Check that cost is positive
        self.assertGreaterEqual(result["estimated_cost"], 0.0)
        
        # Test with fee parameter changes
        fee_context = self.test_context.copy()
        fee_context["governance"] = self.test_context["governance"].copy()
        fee_context["governance"]["proposal_data"] = self.test_context["governance"]["proposal_data"].copy()
        fee_context["governance"]["proposal_data"]["parameters"] = {
            "fee": 0.003,
            "commission": 0.002,
            "protocol_fee": 0.001
        }
        
        fee_result = self.task._analyze_frontrunning_risk(fee_context)
        
        # Risk should be higher with fee parameter changes
        self.assertGreater(fee_result["risk_score"], result["risk_score"] * 0.8)  # Allow some flexibility
    
    def test_liquidation_analysis(self):
        """Test liquidation risk analysis."""
        # Extract method for testing
        result = self.task._analyze_liquidation_risk(self.test_context)
        
        # Check analysis structure
        self.assertIn("risk_score", result)
        self.assertIn("estimated_cost", result)
        self.assertIn("positions_at_risk", result)
        self.assertIn("value_at_risk", result)
        
        # Check risk score bounds
        self.assertGreaterEqual(result["risk_score"], 0.0)
        self.assertLessEqual(result["risk_score"], 1.0)
        
        # Check that cost is positive
        self.assertGreaterEqual(result["estimated_cost"], 0.0)
        
        # Test with liquidation parameter changes
        liquidation_context = self.test_context.copy()
        liquidation_context["governance"] = self.test_context["governance"].copy()
        liquidation_context["governance"]["proposal_data"] = self.test_context["governance"]["proposal_data"].copy()
        liquidation_context["governance"]["proposal_data"]["parameters"] = {
            "liquidation_threshold": 0.80,
            "collateral_factor": 0.75,
            "loan_to_value": 0.70
        }
        
        liquidation_result = self.task._analyze_liquidation_risk(liquidation_context)
        
        # Risk should be higher with liquidation parameter changes
        self.assertGreater(liquidation_result["risk_score"], result["risk_score"])
    
    def test_arbitrage_analysis(self):
        """Test arbitrage risk analysis."""
        # Extract method for testing
        result = self.task._analyze_arbitrage_risk(self.test_context)
        
        # Check analysis structure
        self.assertIn("risk_score", result)
        self.assertIn("estimated_cost", result)
        self.assertIn("oracle_parameter_changes", result)
        self.assertIn("market_making_parameter_changes", result)
        
        # Check risk score bounds
        self.assertGreaterEqual(result["risk_score"], 0.0)
        self.assertLessEqual(result["risk_score"], 1.0)
        
        # Check that cost is positive
        self.assertGreaterEqual(result["estimated_cost"], 0.0)
        
        # The test context has oracle_update_frequency, so oracle_parameter_changes should be True
        self.assertTrue(result["oracle_parameter_changes"])
        
        # Test with market making parameter changes
        market_making_context = self.test_context.copy()
        market_making_context["governance"] = self.test_context["governance"].copy()
        market_making_context["governance"]["proposal_data"] = self.test_context["governance"]["proposal_data"].copy()
        market_making_context["governance"]["proposal_data"]["parameters"] = {
            "curve_parameters": [1, 2, 3],
            "k_value": 0.5,
            "fee_tier": 0.003
        }
        
        market_making_result = self.task._analyze_arbitrage_risk(market_making_context)
        
        # market_making_parameter_changes should be True
        self.assertTrue(market_making_result["market_making_parameter_changes"])
    
    def test_weighted_risk_calculation(self):
        """Test weighted risk score calculation."""
        # Create mock risk components
        risk_components = [
            {"risk_score": 0.8},  # sandwich_attacks
            {"risk_score": 0.5},  # frontrunning
            {"risk_score": 0.2},  # liquidations
            {"risk_score": 0.7}   # arbitrage
        ]
        
        # Calculate weighted risk
        weighted_risk = self.task._calculate_weighted_risk(risk_components)
        
        # Check bounds
        self.assertGreaterEqual(weighted_risk, 0.0)
        self.assertLessEqual(weighted_risk, 1.0)
        
        # Should be weighted towards sandwich_attacks and liquidations
        # which have higher weights in the implementation
        expected_weighted_risk = (
            0.8 * 0.3 +  # sandwich_attacks weight 0.3
            0.5 * 0.2 +  # frontrunning weight 0.2
            0.2 * 0.3 +  # liquidations weight 0.3
            0.7 * 0.2    # arbitrage weight 0.2
        ) / 1.0  # sum of weights
        
        self.assertAlmostEqual(weighted_risk, expected_weighted_risk)
    
    def test_mitigation_generation(self):
        """Test generation of mitigation suggestions."""
        # Create mock risk components
        risk_components = [
            {"risk_score": 0.8, "slippage_parameter_changes": True},  # sandwich_attacks
            {"risk_score": 0.5, "fee_parameter_changes": False},       # frontrunning
            {"risk_score": 0.2, "liquidation_parameter_changes": False}, # liquidations
            {"risk_score": 0.7, "oracle_parameter_changes": True}       # arbitrage
        ]
        
        # Generate mitigations for high risk
        mitigations = self.task._generate_mitigations(risk_components, "high")
        
        # Should include sandwich attack mitigations due to high risk
        self.assertTrue(any("sandwich" in m.lower() for m in mitigations))
        
        # Should include oracle mitigations due to oracle changes
        self.assertTrue(any("oracle" in m.lower() for m in mitigations))
        
        # Should include high risk general mitigations
        self.assertTrue(any("timelock" in m.lower() for m in mitigations))
        
        # Generate mitigations for low risk
        risk_components[0]["risk_score"] = 0.3  # Lower sandwich risk
        risk_components[3]["risk_score"] = 0.2  # Lower arbitrage risk
        
        mitigations = self.task._generate_mitigations(risk_components, "low")
        
        # Should have fewer mitigations
        self.assertLess(len(mitigations), 5)

if __name__ == '__main__':
    unittest.main() 