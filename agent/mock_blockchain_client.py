"""
Mock Blockchain Client

This module provides a mock blockchain client for testing the governance analyst agent.
"""

import logging
import random
import time
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class MockBlockchainClient:
    """
    Mock blockchain client for testing the governance analyst agent.
    """
    
    def __init__(self, network: str = "ethereum"):
        """
        Initialize the mock blockchain client.
        
        Args:
            network: Blockchain network name
        """
        self.network = network
        logger.info(f"Initialized mock blockchain client for {network}")
        
        # Initialize with some mock data
        self._initialize_mock_data()
    
    def _initialize_mock_data(self):
        """Initialize mock blockchain data."""
        self.blocks = []
        self.gas_prices = []
        self.proposals = []
        self.mempool = {}
        self.parameters = {}
        self.trading_pairs = []
        self.pool_liquidity = {}
        self.volume_data = {}
        self.active_bots = []
        
        # Generate mock blocks
        self._generate_mock_blocks(500)
        
        # Generate mock gas prices
        self._generate_mock_gas_prices(200)
        
        # Generate mock proposals
        self._generate_mock_proposals(5)
        
        # Generate mock mempool data
        self._generate_mock_mempool()
        
        # Generate mock protocol parameters
        self._generate_mock_parameters()
        
        # Generate mock trading data
        self._generate_mock_trading_data()
    
    def _generate_mock_blocks(self, count: int = 500):
        """Generate mock block data."""
        base_timestamp = int(time.time()) - count * 12  # 12-second blocks
        base_gas_used = 12000000
        
        for i in range(count):
            # Random variations in block data
            gas_used = base_gas_used + random.randint(-2000000, 2000000)
            block_number = 1000000 + i
            
            self.blocks.append({
                "number": block_number,
                "hash": f"0x{random.getrandbits(256):064x}",
                "timestamp": base_timestamp + i * 12,
                "gasUsed": gas_used,
                "gasLimit": 15000000,
                "baseFeePerGas": 20 + random.randint(0, 30),
                "difficulty": 2,
                "totalDifficulty": "0x1",
                "size": 50000 + random.randint(0, 20000),
                "transactions": [f"0x{random.getrandbits(256):064x}" for _ in range(random.randint(50, 200))]
            })
    
    def _generate_mock_gas_prices(self, count: int = 200):
        """Generate mock gas price data."""
        base_gas = 20  # Base gas price in gwei
        
        for i in range(count):
            # Generate gas price with some volatility
            if i > 0:
                # Add some random walk
                change = random.randint(-5, 5)
                # Ensure gas price doesn't go below 5
                gas_price = max(5, self.gas_prices[-1] + change)
            else:
                gas_price = base_gas
                
            self.gas_prices.append(gas_price)
    
    def _generate_mock_proposals(self, count: int = 5):
        """Generate mock governance proposals."""
        proposal_types = ["fee_change", "parameter_update", "protocol_upgrade", "emergency_fix"]
        statuses = ["active", "pending", "executed", "cancelled", "defeated"]
        
        for i in range(count):
            proposal_type = random.choice(proposal_types)
            status = random.choice(statuses)
            
            # Generate proposal parameters based on type
            if proposal_type == "fee_change":
                parameters = {
                    "fee": 0.003 if random.random() > 0.5 else 0.005,
                    "fee_recipient": f"0x{random.getrandbits(160):040x}"
                }
            elif proposal_type == "parameter_update":
                parameters = {
                    "max_slippage": random.uniform(0.01, 0.05),
                    "liquidation_threshold": random.uniform(0.75, 0.90),
                    "oracle_update_frequency": random.choice([60, 300, 600, 1800])
                }
            elif proposal_type == "protocol_upgrade":
                parameters = {
                    "new_implementation": f"0x{random.getrandbits(160):040x}",
                    "bytecode": f"0x{''.join(random.choices('0123456789abcdef', k=1000))}"
                }
            else:  # emergency_fix
                parameters = {
                    "pause_trading": random.choice([True, False]),
                    "max_withdrawal": random.randint(10000, 1000000)
                }
            
            self.proposals.append({
                "id": f"proposal-{i+1}",
                "title": f"Mock Proposal {i+1}: {proposal_type.replace('_', ' ').title()}",
                "description": f"This is a mock {proposal_type} proposal for testing",
                "proposer": f"0x{random.getrandbits(160):040x}",
                "status": status,
                "created_at": int(time.time()) - random.randint(0, 86400 * 30),  # Up to 30 days old
                "type": proposal_type,
                "parameters": parameters,
                "votes_for": random.randint(1000, 10000),
                "votes_against": random.randint(100, 5000),
                "quorum": 5000,
                "expiration": int(time.time()) + random.randint(86400, 86400 * 7)  # 1-7 days
            })
    
    def _generate_mock_mempool(self):
        """Generate mock mempool data."""
        tx_count = random.randint(2000, 8000)
        avg_gas_price = self.gas_prices[-1] if self.gas_prices else 25
        
        self.mempool = {
            "transaction_count": tx_count,
            "average_gas_price": avg_gas_price + random.randint(-5, 10),
            "high_priority_count": int(tx_count * 0.2),
            "average_transaction_value": random.uniform(0.1, 2.0),
            "total_pending_value": tx_count * random.uniform(0.1, 0.5),
            "max_gas_price": avg_gas_price + random.randint(10, 50),
            "min_gas_price": max(1, avg_gas_price - random.randint(5, 15))
        }
    
    def _generate_mock_parameters(self):
        """Generate mock protocol parameters."""
        self.parameters = {
            "fee": {
                "current_value": 0.003,
                "safe_range": [0.001, 0.01],
                "description": "Protocol fee percentage",
                "last_updated": int(time.time()) - random.randint(86400, 86400 * 30)
            },
            "max_slippage": {
                "current_value": 0.03,
                "safe_range": [0.01, 0.05],
                "description": "Maximum allowed slippage",
                "last_updated": int(time.time()) - random.randint(86400, 86400 * 15)
            },
            "liquidation_threshold": {
                "current_value": 0.825,
                "safe_range": [0.75, 0.90],
                "description": "Collateral liquidation threshold",
                "last_updated": int(time.time()) - random.randint(86400, 86400 * 60)
            },
            "oracle_update_frequency": {
                "current_value": 300,
                "safe_range": [60, 1800],
                "description": "Oracle price update frequency in seconds",
                "last_updated": int(time.time()) - random.randint(86400, 86400 * 45)
            },
            "debt_ceiling": {
                "current_value": 10000000,
                "safe_range": [1000000, 50000000],
                "description": "Maximum protocol debt",
                "last_updated": int(time.time()) - random.randint(86400, 86400 * 20)
            },
            "collateral_factor": {
                "current_value": 0.75,
                "safe_range": [0.5, 0.85],
                "description": "Collateral factor for borrowing",
                "last_updated": int(time.time()) - random.randint(86400, 86400 * 40)
            }
        }
    
    def _generate_mock_trading_data(self):
        """Generate mock trading data."""
        pair_symbols = ["ETH/USDC", "WBTC/USDC", "ETH/WBTC", "LINK/ETH", "UNI/USDC"]
        
        # Generate trading pairs
        for i, symbol in enumerate(pair_symbols):
            token0, token1 = symbol.split("/")
            volatility = random.uniform(0.05, 0.3)
            
            self.trading_pairs.append({
                "id": f"pair-{i+1}",
                "symbol": symbol,
                "token0": token0,
                "token1": token1,
                "volatility": volatility,
                "avg_slippage": random.uniform(0.001, 0.01),
                "fee_tier": random.choice([0.0005, 0.003, 0.01])
            })
        
        # Generate liquidity and volume data
        for pair in self.trading_pairs:
            pair_id = pair["id"]
            # Liquidity between 100K and 10M
            self.pool_liquidity[pair_id] = random.uniform(100000, 10000000)
            # Daily volume between 10K and 5M
            self.volume_data[pair_id] = random.uniform(10000, 5000000)
        
        # Generate active bots
        bot_types = ["arbitrage", "liquidation", "market_making", "sandwich"]
        for i in range(random.randint(5, 20)):
            bot_type = random.choice(bot_types)
            capabilities = {
                "frontrunning": bot_type in ["arbitrage", "sandwich"],
                "backrunning": bot_type in ["arbitrage", "liquidation"],
                "sandwich_attack": bot_type == "sandwich",
                "liquidation": bot_type == "liquidation"
            }
            
            self.active_bots.append({
                "id": f"bot-{i+1}",
                "type": bot_type,
                "capabilities": capabilities,
                "active_since": int(time.time()) - random.randint(3600, 86400 * 180),
                "success_rate": random.uniform(0.5, 0.95)
            })
    
    # Public API methods
    def get_recent_blocks(self, count: int = 100) -> List[Dict[str, Any]]:
        """
        Get the most recent blocks.
        
        Args:
            count: Number of recent blocks to fetch
            
        Returns:
            List of block data
        """
        # Generate more detailed mock blocks
        if not self.blocks:
            latest_block_number = 17_000_000
            self.blocks = []
            
            for i in range(count):
                block_number = latest_block_number - i
                
                # Generate random miner address
                miner = f"0x{random.randint(0, 0xffffffffffffffffffffffffffffffffffffffff):040x}"
                
                # Generate realistic gas parameters
                gas_limit = random.randint(12_000_000, 30_000_000)
                gas_used = int(gas_limit * random.uniform(0.1, 0.95))
                
                # Random number of transactions (0-300)
                tx_count = random.randint(5, 300)
                
                # Base fee per gas (EIP-1559) in wei
                base_fee_per_gas = random.randint(5_000_000_000, 50_000_000_000)
                
                # Generate mock block
                block = {
                    "number": block_number,
                    "hash": f"0x{random.randint(0, 0xffffffffffffffffffffffffffffffffffffffff):064x}",
                    "timestamp": int(time.time()) - i * 12,  # 12 second blocks
                    "miner": miner,
                    "gasUsed": gas_used,
                    "gasLimit": gas_limit,
                    "baseFeePerGas": base_fee_per_gas,
                    "transaction_count": tx_count,
                    "difficulty": random.randint(1_000_000, 10_000_000),
                    "totalDifficulty": random.randint(1_000_000_000, 10_000_000_000),
                    "transactions": [f"0x{random.randint(0, 0xffffffffffffffffffffffffffffffffffffffff):064x}" for _ in range(tx_count)]
                }
                self.blocks.append(block)
        
        return self.blocks[:min(count, len(self.blocks))]
    
    def get_gas_prices(self, block_count: int = 100) -> List[int]:
        """
        Get historical gas prices.
        
        Args:
            block_count: Number of blocks to consider
            
        Returns:
            List of gas prices (gwei)
        """
        # Generate realistic gas price fluctuations around a median value
        base_gas = 25  # Base gas price in gwei
        gas_prices = []
        
        for i in range(block_count):
            # Add some random variation
            variation = random.randint(-10, 15)
            gas_price = max(1, base_gas + variation)
            gas_prices.append(gas_price)
            
            # Occasionally spike or drop gas price to simulate real-world conditions
            if random.random() < 0.05:  # 5% chance of spike
                gas_prices.append(gas_price * random.uniform(1.5, 3.0))
            elif random.random() < 0.05:  # 5% chance of drop
                gas_prices.append(gas_price * random.uniform(0.5, 0.8))
        
        # Ensure we return exactly block_count values
        return gas_prices[:block_count]
    
    def get_governance_proposals(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """
        Get governance proposals.
        
        Args:
            active_only: Whether to fetch only active proposals
            
        Returns:
            List of governance proposals
        """
        if active_only:
            return [p for p in self.proposals if p["status"] in ["active", "pending"]]
        return self.proposals
    
    def get_mempool_data(self) -> Dict[str, Any]:
        """
        Get current mempool data.
        
        Returns:
            Mempool statistics and data
        """
        return self.mempool
    
    def get_protocol_parameters(self) -> Dict[str, Any]:
        """
        Get current protocol parameters.
        
        Returns:
            Protocol parameters with metadata
        """
        return self.parameters
    
    def get_trading_pairs(self) -> List[Dict[str, Any]]:
        """
        Get trading pairs data.
        
        Returns:
            List of trading pairs
        """
        return self.trading_pairs
    
    def get_pool_liquidity(self) -> Dict[str, float]:
        """
        Get pool liquidity data.
        
        Returns:
            Mapping of pair IDs to liquidity values
        """
        return self.pool_liquidity
    
    def get_volume_data(self) -> Dict[str, float]:
        """
        Get trading volume data.
        
        Returns:
            Mapping of pair IDs to volume values
        """
        return self.volume_data
    
    def get_active_bots(self) -> List[Dict[str, Any]]:
        """
        Get active trading bots.
        
        Returns:
            List of active bots
        """
        return self.active_bots
    
    def get_account_history(self, address: str) -> Dict[str, Any]:
        """
        Get account history for a given address.
        
        Args:
            address: Ethereum address
            
        Returns:
            Account history data
        """
        # Generate mock account history
        history = {
            "address": address,
            "first_tx_block": self.blocks[-random.randint(10, 400)]["number"],
            "age_in_blocks": random.randint(100, 10000),
            "transaction_count": random.randint(10, 1000),
            "eth_balance": random.uniform(0.1, 100),
            "proposals": []
        }
        
        # Add some proposals if the account has any
        proposal_count = random.randint(0, 3)
        for i in range(proposal_count):
            status = random.choice(["executed", "rejected", "pending"])
            history["proposals"].append({
                "id": f"prop-{random.randint(1000, 9999)}",
                "status": status,
                "created_at": int(time.time()) - random.randint(86400, 86400 * 60)
            })
        
        return history
    
    def get_contract_bytecode(self, address: str) -> str:
        """
        Get contract bytecode for a given address.
        
        Args:
            address: Contract address
            
        Returns:
            Contract bytecode
        """
        # Generate mock bytecode (just a placeholder)
        return f"0x{''.join(random.choices('0123456789abcdef', k=2000))}"
    
    def get_all_contracts(self) -> Dict[str, str]:
        """
        Get all known contract bytecodes.
        
        Returns:
            Mapping of contract names to bytecodes
        """
        contracts = {}
        contract_names = ["Vault", "Governor", "Token", "Oracle", "AMM", "Staking"]
        
        for name in contract_names:
            contracts[name] = f"0x{''.join(random.choices('0123456789abcdef', k=2000))}"
        
        return contracts 