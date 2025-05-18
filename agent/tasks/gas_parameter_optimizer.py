"""
Gas Parameter Optimizer Task

This task analyzes historical gas usage patterns and recommends optimal
gas parameters for governance proposals.
"""

import logging
from typing import Dict, List, Any, Optional
import statistics
from agent.task_registry import Task, register_task
import random
import time

logger = logging.getLogger(__name__)

@register_task
class GasParameterOptimizer(Task):
    """
    Analyzes historical gas usage and recommends optimal gas parameters
    for governance proposals to minimize transaction costs while ensuring
    timely execution.
    """
    
    task_type = "gas_optimization"
    
    def __init__(self, task_id: Optional[str] = None, parameters: Optional[Dict[str, Any]] = None):
        """Initialize the gas parameter optimizer task."""
        super().__init__(task_id, parameters)
        self.parameters = parameters or {
            "sample_size": 200,
            "percentile_base": 75,
            "volatility_factor": 1.2,
            "min_gas_limit": 100000,
            "max_recommendation_age_blocks": 10,
        }
    
    def requires(self) -> Dict[str, List[str]]:
        """
        Define the data requirements for this task.
        
        Returns:
            Data requirements by category
        """
        return {
            "blockchain": ["recent_blocks", "gas_prices", "transaction_history"],
            "governance": ["proposal_types", "voting_contract_address"],
            "context": ["network_congestion"]
        }
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the gas parameter optimization analysis.
        
        Args:
            context: Execution context with required data
            
        Returns:
            Gas parameter recommendations
        """
        logger.info(f"Executing gas parameter optimization with parameters: {self.parameters}")
        
        # Extract required data
        blockchain_data = context.get("blockchain", {})
        recent_blocks = blockchain_data.get("recent_blocks", [])
        gas_prices = blockchain_data.get("gas_prices", [])
        
        # Check if we have enough data to proceed
        if not gas_prices:
            logger.warning("No gas price data available, using fallback gas prices")
            # Generate fallback gas prices
            gas_prices = [25 + random.randint(-5, 5) for _ in range(10)]
        
        if not recent_blocks:
            logger.warning("No block data available, using fallback block data")
            # Generate a single fallback block
            recent_blocks = [{
                "gasUsed": 12500000,
                "gasLimit": 30000000,
                "number": 1
            }]
        
        # Calculate recommended gas parameters
        try:
            result = self._calculate_recommendations(recent_blocks, gas_prices, context)
            logger.info(f"Gas parameter optimization completed successfully: {result}")
            return {
                "success": True,
                "recommendations": result,
                "metadata": {
                    "analyzed_blocks": len(recent_blocks),
                    "analysis_timestamp": context.get("timestamp", int(time.time())),
                    "network": context.get("network", "ethereum")
                }
            }
        except Exception as e:
            logger.error(f"Error in gas parameter optimization: {e}")
            return {
                "success": False,
                "error": str(e),
                "recommendations": None
            }
    
    def _calculate_recommendations(self, 
                                 recent_blocks: List[Dict[str, Any]], 
                                 gas_prices: List[int],
                                 context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate gas parameter recommendations based on historical data.
        
        Args:
            recent_blocks: List of recent block data
            gas_prices: List of recent gas prices in gwei
            context: Additional execution context
            
        Returns:
            Gas parameter recommendations
        """
        # Extract gas used from blocks
        gas_used = [block.get("gasUsed", 0) for block in recent_blocks if "gasUsed" in block]
        
        # Limit sample size
        sample_size = min(len(gas_used), self.parameters["sample_size"])
        gas_used = gas_used[:sample_size]
        gas_prices = gas_prices[:sample_size]
        
        # Calculate statistics
        if not gas_used or not gas_prices:
            raise ValueError("Insufficient gas data for analysis")
            
        avg_gas_used = statistics.mean(gas_used)
        median_gas_used = statistics.median(gas_used)
        
        # Sort gas prices
        sorted_prices = sorted(gas_prices)
        
        # Calculate percentile for recommended gas price
        percentile_idx = int(len(sorted_prices) * (self.parameters["percentile_base"] / 100))
        recommended_gas_price = sorted_prices[percentile_idx]
        
        # Apply volatility factor for max gas price
        max_gas_price = int(recommended_gas_price * self.parameters["volatility_factor"])
        
        # Network congestion factor (0.0 to 1.0)
        congestion = context.get("network_congestion", 0.5)
        
        # Calculate gas limit with safety margin
        proposal_type = context.get("proposal_type", "standard")
        proposal_type_multipliers = {
            "standard": 1.0,
            "complex": 1.5,
            "upgrade": 2.0
        }
        
        type_multiplier = proposal_type_multipliers.get(proposal_type, 1.0)
        gas_limit_base = max(avg_gas_used * 1.5, self.parameters["min_gas_limit"])
        gas_limit = int(gas_limit_base * type_multiplier * (1 + congestion * 0.5))
        
        # Generate recommendations
        return {
            "gas_price": {
                "recommended": recommended_gas_price,
                "max": max_gas_price,
                "unit": "gwei"
            },
            "gas_limit": gas_limit,
            "estimated_cost_eth": (gas_limit * recommended_gas_price) / 1e9,
            "priority_fee": int(recommended_gas_price * 0.15),
            "recommendation_quality": self._calculate_recommendation_quality(gas_used, gas_prices),
            "proposal_type": proposal_type,
            "validity_blocks": self.parameters["max_recommendation_age_blocks"]
        }
    
    def _calculate_recommendation_quality(self, gas_used: List[int], gas_prices: List[int]) -> str:
        """
        Calculate the quality of the recommendation based on data consistency.
        
        Args:
            gas_used: Gas used in blocks
            gas_prices: Gas prices
            
        Returns:
            Recommendation quality: "high", "medium", or "low"
        """
        # Calculate relative standard deviation as a measure of volatility
        if not gas_used or not gas_prices:
            return "low"
            
        try:
            gas_used_stdev = statistics.stdev(gas_used)
            gas_used_mean = statistics.mean(gas_used)
            gas_used_rsd = (gas_used_stdev / gas_used_mean) if gas_used_mean > 0 else float('inf')
            
            gas_price_stdev = statistics.stdev(gas_prices)
            gas_price_mean = statistics.mean(gas_prices)
            gas_price_rsd = (gas_price_stdev / gas_price_mean) if gas_price_mean > 0 else float('inf')
            
            # Determine quality based on relative standard deviation
            if gas_used_rsd < 0.1 and gas_price_rsd < 0.2:
                return "high"
            elif gas_used_rsd < 0.3 and gas_price_rsd < 0.5:
                return "medium"
            else:
                return "low"
        except statistics.StatisticsError:
            return "low" 