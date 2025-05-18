"""
MEV Cost Estimator Task

This task estimates the potential MEV (Maximal Extractable Value) costs 
associated with governance proposals or parameter changes.
"""

import logging
import math
import time
from typing import Dict, List, Any, Optional
from agent.task_registry import Task, register_task

logger = logging.getLogger(__name__)

@register_task
class MEVCostEstimator(Task):
    """
    Analyzes governance proposals or parameter changes to estimate potential
    MEV extraction costs from frontrunning, sandwich attacks, and other MEV strategies.
    """
    
    task_type = "security_analysis"
    
    def __init__(self, task_id: Optional[str] = None, parameters: Optional[Dict[str, Any]] = None):
        """Initialize the MEV cost estimator task."""
        super().__init__(task_id, parameters)
        self.parameters = parameters or {
            "block_time_seconds": 12,
            "mev_estimation_blocks": 100,
            "liquidation_risk_threshold": 0.2,
            "sandwich_attack_sensitivity": 0.5,
            "volume_impact_factor": 0.65,
            "max_slippage_tolerance": 0.03
        }
    
    def requires(self) -> Dict[str, List[str]]:
        """
        Define the data requirements for this task.
        
        Returns:
            Data requirements by category
        """
        return {
            "blockchain": [
                "recent_blocks",
                "gas_prices",
                "mempool_data"
            ],
            "governance": [
                "proposal_data",
                "protocol_parameters"
            ],
            "defi": [
                "trading_pairs",
                "pool_liquidity",
                "volume_data",
                "active_bots"
            ]
        }
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the MEV cost estimation analysis.
        
        Args:
            context: Execution context with required data
            
        Returns:
            MEV cost estimation results
        """
        logger.info(f"Executing MEV cost estimator with parameters: {self.parameters}")
        
        # Extract data from the appropriate context structure
        blockchain = context.get("blockchain", {})
        governance = context.get("governance", {})
        defi = context.get("defi", {})
        
        # Extract and validate required data
        proposal_data = governance.get("proposal_data")
        if not proposal_data:
            logger.warning("No proposal data provided for MEV analysis, using mock data")
            # Create mock proposal data if missing
            proposal_data = {
                "id": "mock-proposal-1",
                "type": "parameter_update",
                "parameters": {
                    "fee": 0.003,
                    "slippage_tolerance": 0.01,
                    "oracle_update_frequency": 60
                },
                "proposer": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
                "description": "Update protocol fee structure and oracle update frequency"
            }
            governance["proposal_data"] = proposal_data
        
        # Create mock trading pairs if missing
        if "trading_pairs" not in defi or not defi["trading_pairs"]:
            defi["trading_pairs"] = [
                {"id": "ETH/USDC", "volatility": 0.15, "avg_slippage": 0.005},
                {"id": "WBTC/ETH", "volatility": 0.12, "avg_slippage": 0.008},
                {"id": "DAI/USDC", "volatility": 0.01, "avg_slippage": 0.001}
            ]
        
        # Create mock liquidity data if missing
        if "pool_liquidity" not in defi or not defi["pool_liquidity"]:
            defi["pool_liquidity"] = {
                "ETH/USDC": 1000000,
                "WBTC/ETH": 750000,
                "DAI/USDC": 2000000
            }
        
        # Create mock volume data if missing
        if "volume_data" not in defi or not defi["volume_data"]:
            defi["volume_data"] = {
                "ETH/USDC": 500000,
                "WBTC/ETH": 300000,
                "DAI/USDC": 600000
            }
        
        # Create mock active bots if missing
        if "active_bots" not in defi or not defi["active_bots"]:
            defi["active_bots"] = [
                {"id": "bot1", "capabilities": {"frontrunning": True}},
                {"id": "bot2", "capabilities": {"frontrunning": False}},
                {"id": "bot3", "capabilities": {"frontrunning": True}},
                {"id": "bot4", "capabilities": {"frontrunning": True}}
            ]
        
        # Create a clean context with all the required data
        enriched_context = {
            "proposal_data": proposal_data,
            "trading_pairs": defi["trading_pairs"],
            "pool_liquidity": defi["pool_liquidity"],
            "volume_data": defi["volume_data"],
            "active_bots": defi["active_bots"],
            "mempool_data": blockchain.get("mempool_data", {"transaction_count": 1000, "average_transaction_value": 0.5}),
            "gas_prices": blockchain.get("gas_prices", [25]),
            "recent_blocks": blockchain.get("recent_blocks", []),
            "timestamp": context.get("timestamp", int(time.time()))
        }
        
        try:
            # Analyze different MEV vectors
            sandwich_attack_risk = self._analyze_sandwich_attack_risk(enriched_context)
            frontrunning_risk = self._analyze_frontrunning_risk(enriched_context)
            liquidation_risk = self._analyze_liquidation_risk(enriched_context)
            arb_risk = self._analyze_arbitrage_risk(enriched_context)
            
            # Combine risk assessments
            total_mev_cost = (
                sandwich_attack_risk["estimated_cost"] +
                frontrunning_risk["estimated_cost"] +
                liquidation_risk["estimated_cost"] +
                arb_risk["estimated_cost"]
            )
            
            # Calculate weighted risk score
            risk_components = [
                sandwich_attack_risk,
                frontrunning_risk,
                liquidation_risk,
                arb_risk
            ]
            
            weighted_risk_score = self._calculate_weighted_risk(risk_components)
            
            # Determine risk level
            if weighted_risk_score > 0.7:
                risk_level = "high"
            elif weighted_risk_score > 0.3:
                risk_level = "medium"
            else:
                risk_level = "low"
                
            mitigations = self._generate_mitigations(risk_components, risk_level)
            
            logger.info(f"MEV cost estimation completed with risk level: {risk_level}")
            return {
                "success": True,
                "risk_level": risk_level,
                "risk_score": weighted_risk_score,
                "estimated_total_mev_cost": total_mev_cost,
                "estimated_cost_per_block": total_mev_cost / self.parameters["mev_estimation_blocks"],
                "mev_vectors": {
                    "sandwich_attacks": sandwich_attack_risk,
                    "frontrunning": frontrunning_risk,
                    "liquidations": liquidation_risk,
                    "arbitrage": arb_risk
                },
                "mitigations": mitigations,
                "recommendations": mitigations,  # Add recommendations for consistency with other tasks
                "metadata": {
                    "proposal_id": proposal_data.get("id"),
                    "analysis_timestamp": enriched_context.get("timestamp", 0),
                    "estimation_horizon_blocks": self.parameters["mev_estimation_blocks"]
                }
            }
        except Exception as e:
            logger.error(f"Error in MEV cost estimation: {e}")
            return {
                "success": False,
                "error": str(e),
                "mev_risk": "unknown"
            }
    
    def _analyze_sandwich_attack_risk(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze risk and potential cost of sandwich attacks.
        
        Args:
            context: Execution context
            
        Returns:
            Sandwich attack risk assessment
        """
        # Extract data from context
        trading_pairs = context.get("trading_pairs", [])
        proposal_data = context.get("proposal_data", {})
        liquidity_data = context.get("pool_liquidity", {})
        volume_data = context.get("volume_data", {})
        
        # Proposal parameter changes relevant to sandwich attacks
        parameter_changes = proposal_data.get("parameters", {})
        slippage_changes = any(
            param in parameter_changes for param in 
            ["slippage_tolerance", "max_slippage", "min_output_amount"]
        )
        
        # Calculate base sensitivity
        sensitivity = self.parameters["sandwich_attack_sensitivity"]
        if slippage_changes:
            sensitivity *= 1.5
        
        # Calculate risk for each trading pair
        pair_risks = []
        for pair in trading_pairs:
            pair_id = pair.get("id", "unknown")
            liquidity = liquidity_data.get(pair_id, 0)
            volume = volume_data.get(pair_id, 0)
            
            if liquidity <= 0 or volume <= 0:
                continue
                
            # Calculate volatility index as a simple measure
            # In real implementation, this would use historical price data
            volatility = pair.get("volatility", 0.1)
            
            # Turnover ratio as a measure of activity
            turnover_ratio = volume / liquidity if liquidity > 0 else 0
            
            # Calculate risk score for this pair
            pair_risk = (
                sensitivity * 
                volatility * 
                math.sqrt(turnover_ratio) * 
                self.parameters["volume_impact_factor"]
            )
            
            # Calculate potential MEV from sandwich attacks
            # This is a simple model, real implementations would be more complex
            potential_mev = (
                volume * 
                pair_risk * 
                min(self.parameters["max_slippage_tolerance"], pair.get("avg_slippage", 0.01))
            )
            
            pair_risks.append({
                "pair": pair_id,
                "risk_score": pair_risk,
                "potential_mev": potential_mev,
                "volume": volume,
                "liquidity": liquidity
            })
        
        # Calculate total risk and cost
        total_risk = sum(pr["risk_score"] for pr in pair_risks) / len(pair_risks) if pair_risks else 0
        total_cost = sum(pr["potential_mev"] for pr in pair_risks)
        
        return {
            "risk_score": min(total_risk, 1.0),  # Cap at 1.0
            "estimated_cost": total_cost,
            "affected_pairs": len(pair_risks),
            "highest_risk_pairs": sorted(pair_risks, key=lambda x: x["risk_score"], reverse=True)[:3],
            "slippage_parameter_changes": slippage_changes
        }
    
    def _analyze_frontrunning_risk(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze risk and potential cost of transaction frontrunning.
        
        Args:
            context: Execution context
            
        Returns:
            Frontrunning risk assessment
        """
        # Extract data from context
        mempool_data = context.get("mempool_data", {})
        gas_prices = context.get("gas_prices", [])
        proposal_data = context.get("proposal_data", {})
        active_bots = context.get("active_bots", [])
        
        # Get frontrunning-relevant parameters
        parameter_changes = proposal_data.get("parameters", {})
        fee_changes = any(
            param in parameter_changes for param in 
            ["fee", "commission", "tax_rate", "protocol_fee"]
        )
        
        # Calculate average gas price volatility
        if len(gas_prices) > 1:
            gas_price_changes = [abs(gas_prices[i] - gas_prices[i-1]) / gas_prices[i-1] 
                              for i in range(1, len(gas_prices))]
            gas_volatility = sum(gas_price_changes) / len(gas_price_changes) if gas_price_changes else 0
        else:
            gas_volatility = 0
        
        # Count frontrunning-capable bots
        frontrunning_bots = sum(1 for bot in active_bots if bot.get("capabilities", {}).get("frontrunning", False))
        
        # Calculate base risk based on mempool density and gas price volatility
        mempool_tx_count = mempool_data.get("transaction_count", 0)
        mempool_density = min(mempool_tx_count / 5000, 1.0)  # Normalize to [0,1]
        
        # Base risk score
        risk_score = (
            0.4 * mempool_density + 
            0.3 * gas_volatility + 
            0.3 * (frontrunning_bots / max(len(active_bots), 1))
        )
        
        # Increase risk if fee-related parameters are changing
        if fee_changes:
            risk_score *= 1.3
            
        # Calculate potential MEV cost
        # This is a simplified model
        avg_tx_value = mempool_data.get("average_transaction_value", 0)
        potential_mev = (
            mempool_tx_count * 
            avg_tx_value * 
            risk_score * 
            0.005  # Assume 0.5% extraction rate
        )
        
        return {
            "risk_score": min(risk_score, 1.0),  # Cap at 1.0
            "estimated_cost": potential_mev,
            "mempool_density": mempool_density,
            "gas_price_volatility": gas_volatility,
            "frontrunning_bot_prevalence": frontrunning_bots / max(len(active_bots), 1),
            "fee_parameter_changes": fee_changes
        }
    
    def _analyze_liquidation_risk(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze risk and potential cost of liquidation opportunities.
        
        Args:
            context: Execution context
            
        Returns:
            Liquidation risk assessment
        """
        # This would require lending protocol data which we're simulating
        proposal_data = context.get("proposal_data", {})
        
        # Get liquidation-relevant parameters
        parameter_changes = proposal_data.get("parameters", {})
        liquidation_related = any(
            param in parameter_changes for param in 
            ["liquidation_threshold", "collateral_factor", "loan_to_value", "debt_ceiling"]
        )
        
        # Default values for simulation
        simulated_positions_at_risk = 120  # Number of positions
        simulated_value_at_risk = 5000000  # Value in currency units
        simulated_avg_discount = 0.05  # Average liquidation discount
        
        # Base risk determination
        if liquidation_related:
            # Parameter changes that directly affect liquidations
            risk_score = 0.7
            # Estimate affected value based on how much parameters change
            # In real implementation, this would analyze lending protocol positions
            affected_value_pct = 0.15
        else:
            # Indirect effects on liquidations
            risk_score = 0.2
            affected_value_pct = 0.05
        
        # Apply threshold modifier
        if risk_score < self.parameters["liquidation_risk_threshold"]:
            risk_score *= 0.7  # Reduce low risks further
            
        # Calculate potential MEV from liquidations
        potential_mev = (
            simulated_value_at_risk * 
            affected_value_pct * 
            simulated_avg_discount
        )
        
        return {
            "risk_score": min(risk_score, 1.0),  # Cap at 1.0
            "estimated_cost": potential_mev,
            "positions_at_risk": int(simulated_positions_at_risk * affected_value_pct),
            "value_at_risk": simulated_value_at_risk * affected_value_pct,
            "liquidation_parameter_changes": liquidation_related
        }
    
    def _analyze_arbitrage_risk(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze risk and potential cost of arbitrage opportunities.
        
        Args:
            context: Execution context
            
        Returns:
            Arbitrage risk assessment
        """
        # Extract data
        trading_pairs = context.get("trading_pairs", [])
        proposal_data = context.get("proposal_data", {})
        protocol_parameters = context.get("protocol_parameters", {})
        
        # Relevant parameter changes
        parameter_changes = proposal_data.get("parameters", {})
        oracle_changes = any(
            param in parameter_changes for param in 
            ["price_oracle", "oracle_update_frequency", "price_feed"]
        )
        
        market_making_changes = any(
            param in parameter_changes for param in 
            ["curve_parameters", "k_value", "fee_tier", "pool_weights"]
        )
        
        # Calculate base risk
        if oracle_changes:
            # Oracle changes create significant arb risk
            base_risk = 0.8
        elif market_making_changes:
            # Market making parameter changes create moderate arb risk
            base_risk = 0.6
        else:
            # Other changes have lower arb risk
            base_risk = 0.3
            
        # Calculate potential arb opportunities
        # This is a simplified model
        total_daily_volume = sum(context.get("volume_data", {}).values())
        
        # Affected volume percentage based on risk
        affected_volume_pct = base_risk * 0.1  # Max 10% of volume
        
        # Potential profit per arb (as percentage of trade)
        potential_profit_pct = 0.002  # 0.2% profit per arb
        if oracle_changes:
            potential_profit_pct = 0.005  # 0.5% for oracle changes
            
        # Calculate potential MEV
        potential_mev = (
            total_daily_volume * 
            affected_volume_pct * 
            potential_profit_pct * 
            (self.parameters["mev_estimation_blocks"] * self.parameters["block_time_seconds"] / 86400)
        )
        
        return {
            "risk_score": base_risk,
            "estimated_cost": potential_mev,
            "oracle_parameter_changes": oracle_changes,
            "market_making_parameter_changes": market_making_changes,
            "daily_volume": total_daily_volume,
            "affected_volume_percentage": affected_volume_pct
        }
    
    def _calculate_weighted_risk(self, risk_components: List[Dict[str, Any]]) -> float:
        """
        Calculate weighted risk score from component risks.
        
        Args:
            risk_components: List of risk assessments
            
        Returns:
            Weighted risk score between 0.0 and 1.0
        """
        if not risk_components:
            return 0.0
            
        # Component weights
        weights = {
            "sandwich_attacks": 0.3,
            "frontrunning": 0.2,
            "liquidations": 0.3,
            "arbitrage": 0.2
        }
        
        # Calculate weighted sum
        weighted_sum = 0.0
        weight_sum = 0.0
        
        for i, component in enumerate(risk_components):
            component_type = list(weights.keys())[i]
            weight = weights[component_type]
            weighted_sum += component["risk_score"] * weight
            weight_sum += weight
            
        # Normalize
        if weight_sum > 0:
            return weighted_sum / weight_sum
        return 0.0
    
    def _generate_mitigations(self, risk_components: List[Dict[str, Any]], risk_level: str) -> List[str]:
        """
        Generate mitigation suggestions based on MEV risks.
        
        Args:
            risk_components: List of risk assessments
            risk_level: Overall risk level
            
        Returns:
            List of mitigation suggestions
        """
        mitigations = []
        
        # Get components by index
        sandwich_risk = risk_components[0]
        frontrunning_risk = risk_components[1]
        liquidation_risk = risk_components[2]
        arb_risk = risk_components[3]
        
        # Add mitigations based on specific risks
        if sandwich_risk["risk_score"] > 0.6:
            mitigations.append("Consider implementing anti-sandwich protection like Uniswap's")
            mitigations.append("Add minimum output amount requirements for swaps")
            
        if sandwich_risk["slippage_parameter_changes"]:
            mitigations.append("Carefully review slippage parameter changes for sandwich attack vectors")
            
        if frontrunning_risk["risk_score"] > 0.5:
            mitigations.append("Consider implementing a commit-reveal scheme to prevent frontrunning")
            mitigations.append("Implement batch auctions for high-value transactions")
            
        if frontrunning_risk["fee_parameter_changes"]:
            mitigations.append("Phase in fee changes gradually to reduce frontrunning opportunities")
            
        if liquidation_risk["risk_score"] > 0.4:
            mitigations.append("Implement Dutch auctions for liquidations")
            mitigations.append("Consider gradual changes to liquidation parameters")
            
        if arb_risk["oracle_parameter_changes"]:
            mitigations.append("Use time-weighted average prices (TWAPs) to reduce oracle manipulation")
            mitigations.append("Implement circuit breakers for extreme price movements")
            
        # Add general mitigations based on overall risk
        if risk_level == "high":
            mitigations.append("Consider scheduling parameter changes during periods of low network activity")
            mitigations.append("Apply timelock to all parameter changes to allow users to adjust positions")
            mitigations.append("Employ private mempool solutions for critical transactions")
        elif risk_level == "medium":
            mitigations.append("Monitor network activity during and after parameter changes")
            mitigations.append("Consider phased implementation of parameter changes")
            
        # Remove duplicates while preserving order
        unique_mitigations = []
        for mitigation in mitigations:
            if mitigation not in unique_mitigations:
                unique_mitigations.append(mitigation)
                
        return unique_mitigations 