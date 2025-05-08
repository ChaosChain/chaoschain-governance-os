"""
Simulation harness for generating and running mock transactions.

This module provides functionality for generating random EVM transactions
and simulating their execution for proposal validation.
"""

import random
import time
import json
from typing import List, Dict, Any, Tuple, Optional
import uuid

# Import demo configuration
from simulation.harness.config import DEMO_TRANSACTIONS


class SimulationHarness:
    """
    Harness for running simulations of transaction batches.
    
    Generates mock transaction data for testing proposal effects.
    """
    
    # Common ERC20 and DeFi function signatures
    FUNCTION_SIGNATURES = [
        "0xa9059cbb",  # transfer(address,uint256)
        "0x095ea7b3",  # approve(address,uint256)
        "0x23b872dd",  # transferFrom(address,address,uint256)
        "0x70a08231",  # balanceOf(address)
        "0x18160ddd",  # totalSupply()
        "0x7ff36ab5",  # swapExactETHForTokens(uint256,address[],address,uint256)
        "0x38ed1739",  # swapExactTokensForTokens(uint256,uint256,address[],address,uint256)
        "0x5c11d795",  # swapExactTokensForETH(uint256,uint256,address[],address,uint256)
    ]
    
    # Common ERC20 token addresses on Ethereum (can be replaced with Sepolia testnet tokens)
    TOKEN_ADDRESSES = [
        "0xdAC17F958D2ee523a2206206994597C13D831ec7",  # USDT
        "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",  # USDC
        "0x6B175474E89094C44Da98b954EedeAC495271d0F",  # DAI
        "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",  # WBTC
        "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",  # WETH
    ]
    
    def __init__(
        self, 
        transaction_count: int = 100,
        gas_limit: int = 12500000,  # Default Ethereum block gas limit
        base_fee_per_gas: int = 10 * 10**9,  # 10 Gwei
        fee_denominator: int = 5,  # Controls fee volatility
        use_predefined_transactions: bool = False  # Use demo transactions
    ):
        """
        Initialize the simulation harness.
        
        Args:
            transaction_count: Number of transactions to generate
            gas_limit: Total gas limit for the block
            base_fee_per_gas: Base fee per gas in wei
            fee_denominator: Controls fee volatility (higher = more stable)
            use_predefined_transactions: Whether to use predefined transactions instead of generating random ones
        """
        self.transaction_count = transaction_count
        self.gas_limit = gas_limit
        self.base_fee_per_gas = base_fee_per_gas
        self.fee_denominator = fee_denominator
        self.simulation_id = str(uuid.uuid4())
        self.use_predefined_transactions = use_predefined_transactions
    
    def _generate_address(self) -> str:
        """
        Generate a random Ethereum address.
        
        Returns:
            Random Ethereum address
        """
        return "0x" + "".join(random.choices("0123456789abcdef", k=40))
    
    def _generate_value(self, max_value: int = 10 * 10**18) -> int:
        """
        Generate a random transaction value.
        
        Args:
            max_value: Maximum value in wei
            
        Returns:
            Random transaction value
        """
        return random.randint(0, max_value)
    
    def _generate_gas_price(self) -> int:
        """
        Generate a random gas price with some volatility.
        
        Returns:
            Random gas price in wei
        """
        # Add some volatility around the base fee
        volatility = self.base_fee_per_gas // self.fee_denominator
        variation = random.randint(-volatility, volatility)
        gas_price = max(1, self.base_fee_per_gas + variation)
        
        # Add a random priority fee
        priority_fee = random.randint(1 * 10**9, 3 * 10**9)  # 1-3 Gwei
        return gas_price + priority_fee
    
    def _generate_gas_used(self, gas_limit: int = 21000) -> int:
        """
        Generate a random amount of gas used.
        
        Args:
            gas_limit: Gas limit for the transaction
            
        Returns:
            Random gas used
        """
        return random.randint(gas_limit // 2, gas_limit)
    
    def _generate_transaction_data(self) -> str:
        """
        Generate random transaction data.
        
        Returns:
            Random transaction data as a hex string
        """
        # Sometimes generate empty data (simple ETH transfer)
        if random.random() < 0.3:
            return "0x"
        
        # Generate function call data
        function_sig = random.choice(self.FUNCTION_SIGNATURES)
        
        # Generate parameters based on the function signature
        if function_sig == "0xa9059cbb" or function_sig == "0x095ea7b3":
            # transfer or approve: address, uint256
            address = self._generate_address()[2:]  # Remove 0x prefix
            amount = hex(self._generate_value())[2:].zfill(64)
            return f"0x{function_sig}{address.zfill(64)}{amount}"
        elif function_sig == "0x23b872dd":
            # transferFrom: address, address, uint256
            from_addr = self._generate_address()[2:].zfill(64)
            to_addr = self._generate_address()[2:].zfill(64)
            amount = hex(self._generate_value())[2:].zfill(64)
            return f"0x{function_sig}{from_addr}{to_addr}{amount}"
        else:
            # Just use a generic parameter for simplicity
            return f"0x{function_sig}{'0' * 64}"
    
    def generate_transaction(self) -> Dict[str, Any]:
        """
        Generate a single random transaction.
        
        Returns:
            Random transaction object
        """
        from_address = self._generate_address()
        
        # Decide if it's a contract interaction or direct transfer
        is_contract = random.random() < 0.7
        
        if is_contract:
            to_address = random.choice(self.TOKEN_ADDRESSES)
            gas_limit = random.randint(50000, 300000)
            data = self._generate_transaction_data()
        else:
            to_address = self._generate_address()
            gas_limit = 21000  # Standard gas for ETH transfer
            data = "0x"
        
        gas_price = self._generate_gas_price()
        gas_used = self._generate_gas_used(gas_limit)
        
        return {
            "from": from_address,
            "to": to_address,
            "value": hex(self._generate_value()),
            "gasPrice": hex(gas_price),
            "gasLimit": hex(gas_limit),
            "gasUsed": hex(gas_used),
            "data": data,
            "nonce": hex(random.randint(0, 1000)),
            "hash": "0x" + "".join(random.choices("0123456789abcdef", k=64)),
        }
    
    def generate_transactions(self) -> List[Dict[str, Any]]:
        """
        Generate a batch of transactions.
        
        Returns:
            List of transactions
        """
        if self.use_predefined_transactions:
            # Use the predefined demo transactions
            return DEMO_TRANSACTIONS[:self.transaction_count]
        else:
            # Generate random transactions
            return [self.generate_transaction() for _ in range(self.transaction_count)]
    
    def run_simulation(self, proposal_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run a simulation with the given proposal data.
        
        Args:
            proposal_data: Proposal data including changes to simulate
            
        Returns:
            Simulation results
        """
        # Generate transactions
        transactions = self.generate_transactions()
        
        # Simulate gas usage adjustments based on proposal parameters
        gas_factor = 1.0
        fee_factor = 1.0
        
        # Extract parameters from proposal data if available
        if "gas_adjustment" in proposal_data:
            gas_factor = float(proposal_data["gas_adjustment"])
        
        if "fee_adjustment" in proposal_data:
            fee_factor = float(proposal_data["fee_adjustment"])
        
        # Apply adjustments to transactions
        for tx in transactions:
            # Convert hex gas values to int, apply factor, convert back to hex
            gas_limit_int = int(tx["gasLimit"], 16)
            gas_used_int = int(tx["gasUsed"], 16)
            gas_price_int = int(tx["gasPrice"], 16)
            
            adjusted_gas_limit = int(gas_limit_int * gas_factor)
            adjusted_gas_used = int(min(adjusted_gas_limit, gas_used_int * gas_factor))
            adjusted_gas_price = int(gas_price_int * fee_factor)
            
            tx["adjustedGasLimit"] = hex(adjusted_gas_limit)
            tx["adjustedGasUsed"] = hex(adjusted_gas_used)
            tx["adjustedGasPrice"] = hex(adjusted_gas_price)
            
            # Calculate original and adjusted costs
            original_cost = gas_used_int * gas_price_int
            adjusted_cost = adjusted_gas_used * adjusted_gas_price
            
            tx["originalCost"] = hex(original_cost)
            tx["adjustedCost"] = hex(adjusted_cost)
            tx["costDifference"] = hex(adjusted_cost - original_cost)
        
        # Calculate summary statistics
        total_original_gas = sum(int(tx["gasUsed"], 16) for tx in transactions)
        total_adjusted_gas = sum(int(tx["adjustedGasUsed"], 16) for tx in transactions)
        
        total_original_cost = sum(int(tx["originalCost"], 16) for tx in transactions)
        total_adjusted_cost = sum(int(tx["adjustedCost"], 16) for tx in transactions)
        
        avg_original_gas = total_original_gas / len(transactions) if transactions else 0
        avg_adjusted_gas = total_adjusted_gas / len(transactions) if transactions else 0
        
        avg_original_cost = total_original_cost / len(transactions) if transactions else 0
        avg_adjusted_cost = total_adjusted_cost / len(transactions) if transactions else 0
        
        # Gas delta percentage (formatted as string for display)
        gas_delta_percent = ((total_adjusted_gas - total_original_gas) / total_original_gas * 100) if total_original_gas > 0 else 0
        fee_growth_bps = ((fee_factor - 1) * 10000)  # Convert to basis points
        
        # Create simulation result
        result = {
            "simulation_id": self.simulation_id,
            "proposal_id": proposal_data.get("proposal_id", None),
            "timestamp": int(time.time()),
            "transaction_count": len(transactions),
            "gas_limit": self.gas_limit,
            "base_fee_per_gas": self.base_fee_per_gas,
            "fee_denominator": self.fee_denominator,
            "gas_factor": gas_factor,
            "fee_factor": fee_factor,
            "total_original_gas": total_original_gas,
            "total_adjusted_gas": total_adjusted_gas,
            "avg_original_gas": avg_original_gas,
            "avg_adjusted_gas": avg_adjusted_gas,
            "total_original_cost": total_original_cost,
            "total_adjusted_cost": total_adjusted_cost,
            "avg_original_cost": avg_original_cost,
            "avg_adjusted_cost": avg_adjusted_cost,
            "cost_difference": total_adjusted_cost - total_original_cost,
            "cost_difference_percent": (
                ((total_adjusted_cost - total_original_cost) / total_original_cost * 100)
                if total_original_cost > 0 else 0
            ),
            "gas_delta_percent": gas_delta_percent,
            "fee_growth_bps": fee_growth_bps,
            "transactions": transactions,
        }
        
        return result


def create_simulation(
    proposal_data: Dict[str, Any],
    transaction_count: int = 100,
    gas_limit: int = 12500000,
    base_fee_per_gas: int = 10 * 10**9,
    fee_denominator: int = 5,
    use_predefined_transactions: bool = False
) -> Dict[str, Any]:
    """
    Create and run a simulation for the given proposal data.
    
    Args:
        proposal_data: Proposal data to simulate
        transaction_count: Number of transactions to generate
        gas_limit: Total gas limit for the block
        base_fee_per_gas: Base fee per gas in wei
        fee_denominator: Controls fee volatility
        use_predefined_transactions: Whether to use predefined transactions
        
    Returns:
        Simulation results
    """
    harness = SimulationHarness(
        transaction_count=transaction_count,
        gas_limit=gas_limit,
        base_fee_per_gas=base_fee_per_gas,
        fee_denominator=fee_denominator,
        use_predefined_transactions=use_predefined_transactions
    )
    
    return harness.run_simulation(proposal_data) 