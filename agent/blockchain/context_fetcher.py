"""
Blockchain context fetcher for the Ethereum testnet.

This module provides functionality to fetch blockchain data such as recent blocks,
governance proposals, and gas prices from the Ethereum testnet.
"""

import os
import logging
import time
from typing import Dict, List, Any, Optional, Union
import json
from abc import ABC, abstractmethod
import statistics

# Web3 imports - will be imported conditionally to allow for mock mode
try:
    from web3 import Web3
    from web3.middleware import geth_poa_middleware
    WEB3_AVAILABLE = True
except ImportError:
    WEB3_AVAILABLE = False
    logging.warning("Web3 library not available, using mock data only")

# Use environment variable to determine whether to use mock data or real blockchain
USE_MOCK = os.environ.get('ETHEREUM_MOCK', 'true').lower() == 'true'

logger = logging.getLogger(__name__)


class ContextFetcher(ABC):
    """Abstract base class for blockchain context fetchers."""
    
    @abstractmethod
    def get_recent_blocks(self, n: int = 128) -> List[Dict[str, Any]]:
        """Fetch the most recent n blocks."""
        pass
    
    @abstractmethod
    def get_active_governor_proposals(self) -> List[Dict[str, Any]]:
        """Fetch active governance proposals."""
        pass
    
    @abstractmethod
    def get_gas_price_stats(self, block_count: int = 100) -> Dict[str, Any]:
        """Fetch gas price statistics from recent blocks."""
        pass


class EthereumContextFetcher(ContextFetcher):
    """
    Context fetcher implementation for the Ethereum testnet.
    
    This class provides methods to fetch real blockchain data from the Ethereum testnet,
    including recent blocks, governance proposals, and gas price statistics.
    """
    
    def __init__(self, provider_url: Optional[str] = None, chain_id: int = 11155111):
        """
        Initialize the EthereumContextFetcher.
        
        Args:
            provider_url: URL of the Ethereum node to connect to. If None, uses
                         the ETHEREUM_PROVIDER_URL environment variable or a default value.
            chain_id: Chain ID for the Ethereum network. Default is 11155111 (Sepolia).
        """
        if not WEB3_AVAILABLE:
            raise ImportError("Web3 library is required but not available. Install with 'pip install web3'.")
        
        self.provider_url = provider_url or os.environ.get(
            'ETHEREUM_PROVIDER_URL', 
            'https://sepolia.infura.io/v3/9aa3d95b3bc440fa88ea12eaa4456161'  # Public Infura endpoint
        )
        
        self.chain_id = chain_id
        
        # Set up the Web3 connection
        self.web3 = Web3(Web3.HTTPProvider(self.provider_url))
        
        # Apply middleware for PoA networks like Sepolia
        self.web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        
        # Check connection
        if not self.web3.is_connected():
            raise ConnectionError(f"Failed to connect to Ethereum node at {self.provider_url}")
        
        logger.info(f"Connected to Ethereum network: {self.provider_url}")
        logger.info(f"Current block number: {self.web3.eth.block_number}")
        
        # Standard governor ABI fragment for proposal-related functions
        self.governor_abi = [
            {
                "inputs": [],
                "name": "proposalCount",
                "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [{"internalType": "uint256", "name": "proposalId", "type": "uint256"}],
                "name": "state",
                "outputs": [{"internalType": "uint8", "name": "", "type": "uint8"}],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [{"internalType": "uint256", "name": "proposalId", "type": "uint256"}],
                "name": "proposals",
                "outputs": [
                    {"internalType": "uint256", "name": "id", "type": "uint256"},
                    {"internalType": "address", "name": "proposer", "type": "address"},
                    {"internalType": "uint256", "name": "eta", "type": "uint256"},
                    {"internalType": "uint256", "name": "startBlock", "type": "uint256"},
                    {"internalType": "uint256", "name": "endBlock", "type": "uint256"},
                    {"internalType": "uint256", "name": "forVotes", "type": "uint256"},
                    {"internalType": "uint256", "name": "againstVotes", "type": "uint256"},
                    {"internalType": "bool", "name": "canceled", "type": "bool"},
                    {"internalType": "bool", "name": "executed", "type": "bool"}
                ],
                "stateMutability": "view",
                "type": "function"
            }
        ]
        
        # Known governance contracts on the network
        self.governance_contracts = [
            # Example governance contract addresses - should be replaced with real ones
            "0x5991A2dF15A8F6A256D3Ec51E99254Cd3fb576A9",  # Placeholder - replace with real one
        ]
    
    def get_recent_blocks(self, n: int = 128) -> List[Dict[str, Any]]:
        """
        Fetch the most recent n blocks from the Ethereum testnet.
        
        Args:
            n: Number of recent blocks to fetch
            
        Returns:
            List of block data objects
        """
        logger.info(f"Fetching {n} recent blocks from Ethereum network")
        
        latest_block = self.web3.eth.block_number
        blocks = []
        
        for i in range(n):
            if latest_block - i < 0:
                break
                
            try:
                block = self.web3.eth.get_block(latest_block - i, full_transactions=False)
                
                # Convert to serializable format
                block_data = {
                    "number": block.number,
                    "hash": block.hash.hex(),
                    "timestamp": block.timestamp,
                    "miner": block.miner,
                    "gas_used": block.gasUsed,
                    "gas_limit": block.gasLimit,
                    "transaction_count": len(block.transactions),
                    "base_fee_per_gas": getattr(block, "baseFeePerGas", None)
                }
                
                blocks.append(block_data)
            except Exception as e:
                logger.error(f"Error fetching block {latest_block - i}: {e}")
        
        logger.info(f"Fetched {len(blocks)} blocks")
        return blocks
    
    def get_active_governor_proposals(self) -> List[Dict[str, Any]]:
        """
        Fetch active governance proposals from known governance contracts on the Ethereum network.
        
        Returns:
            List of active governance proposals
        """
        logger.info("Fetching active governance proposals from Ethereum network")
        
        active_proposals = []
        
        for contract_address in self.governance_contracts:
            try:
                governor_contract = self.web3.eth.contract(
                    address=self.web3.to_checksum_address(contract_address),
                    abi=self.governor_abi
                )
                
                # Get proposal count (if available in the ABI)
                try:
                    proposal_count = governor_contract.functions.proposalCount().call()
                    logger.info(f"Found {proposal_count} total proposals in contract {contract_address}")
                except Exception as e:
                    logger.warning(f"Could not get proposal count for {contract_address}: {e}")
                    proposal_count = 100  # Use a reasonable maximum to try
                
                # Check the last 10 proposals for active ones
                for proposal_id in range(max(1, proposal_count - 10), proposal_count + 1):
                    try:
                        # Try to get the proposal state
                        state = governor_contract.functions.state(proposal_id).call()
                        
                        # States that indicate an active proposal (varies by implementation)
                        # Typically: 1 = Active, 0 = Pending, 2 = Canceled, 3 = Defeated, 4 = Succeeded, etc.
                        if state in [0, 1]:  # Pending or Active
                            try:
                                # Try to get detailed proposal info if available
                                proposal_data = governor_contract.functions.proposals(proposal_id).call()
                                
                                # Format proposal data based on the contract's structure
                                formatted_proposal = {
                                    "id": proposal_id,
                                    "contract_address": contract_address,
                                    "proposer": proposal_data[1],
                                    "start_block": proposal_data[3],
                                    "end_block": proposal_data[4],
                                    "for_votes": proposal_data[5],
                                    "against_votes": proposal_data[6],
                                    "state": state,
                                    "description": self._get_proposal_description(contract_address, proposal_id)
                                }
                                
                                active_proposals.append(formatted_proposal)
                                logger.info(f"Found active proposal {proposal_id} in contract {contract_address}")
                            except Exception as e:
                                logger.warning(f"Error getting proposal details for {proposal_id}: {e}")
                                
                                # Add minimal proposal data
                                active_proposals.append({
                                    "id": proposal_id,
                                    "contract_address": contract_address,
                                    "state": state,
                                    "description": f"Proposal {proposal_id} (limited data)"
                                })
                    except Exception as e:
                        logger.debug(f"Error checking proposal {proposal_id}: {e}")
            except Exception as e:
                logger.error(f"Error interacting with governance contract {contract_address}: {e}")
        
        # If no real proposals found, provide a mock example for demonstration
        if not active_proposals and not USE_MOCK:
            logger.warning("No active proposals found, using an example proposal")
            active_proposals.append({
                "id": 42,
                "contract_address": self.governance_contracts[0] if self.governance_contracts else "0x0000000000000000000000000000000000000000",
                "proposer": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
                "start_block": self.web3.eth.block_number - 1000,
                "end_block": self.web3.eth.block_number + 1000,
                "for_votes": 1000000,
                "against_votes": 500000,
                "state": 1,
                "description": "Example proposal: Update gas fee mechanism to better handle network congestion"
            })
        
        logger.info(f"Fetched {len(active_proposals)} active governance proposals")
        return active_proposals
    
    def get_gas_price_stats(self, block_count: int = 100) -> Dict[str, Any]:
        """
        Calculate gas price statistics from recent blocks on the Ethereum network.
        
        Args:
            block_count: Number of recent blocks to analyze
            
        Returns:
            Dictionary with gas price statistics
        """
        logger.info(f"Calculating gas price statistics from {block_count} recent blocks")
        
        # Fetch recent blocks
        blocks = self.get_recent_blocks(block_count)
        
        # Extract base fees if available
        base_fees = []
        for block in blocks:
            if block.get("base_fee_per_gas") is not None:
                base_fees.append(block["base_fee_per_gas"])
        
        # Get current gas price
        try:
            current_gas_price = self.web3.eth.gas_price
            # Convert to gwei
            current_gas_price_gwei = current_gas_price / 1e9
        except Exception as e:
            logger.error(f"Error getting current gas price: {e}")
            current_gas_price_gwei = 0
        
        # Calculate statistics if we have data
        if base_fees:
            # Convert to gwei
            base_fees_gwei = [fee / 1e9 for fee in base_fees]
            
            stats = {
                "current_gas_price_gwei": current_gas_price_gwei,
                "mean_base_fee_gwei": statistics.mean(base_fees_gwei),
                "median_base_fee_gwei": statistics.median(base_fees_gwei),
                "min_base_fee_gwei": min(base_fees_gwei),
                "max_base_fee_gwei": max(base_fees_gwei),
                "gas_prices": base_fees_gwei,  # Full list for more detailed analysis
                "block_count": len(base_fees),
                "timestamp": int(time.time())
            }
            
            # Calculate percentiles if we have enough data
            if len(base_fees_gwei) >= 4:
                stats.update({
                    "percentile_25_gwei": statistics.quantiles(base_fees_gwei, n=4)[0],
                    "percentile_50_gwei": statistics.quantiles(base_fees_gwei, n=4)[1],
                    "percentile_75_gwei": statistics.quantiles(base_fees_gwei, n=4)[2]
                })
            
            # Calculate standard deviation if we have enough data
            if len(base_fees_gwei) >= 2:
                stats["stdev_gwei"] = statistics.stdev(base_fees_gwei)
        else:
            # No base fee data available, use current gas price
            stats = {
                "current_gas_price_gwei": current_gas_price_gwei,
                "gas_prices": [current_gas_price_gwei],
                "block_count": 1,
                "timestamp": int(time.time())
            }
        
        logger.info(f"Calculated gas price statistics from {len(base_fees)} blocks")
        return stats
    
    def _get_proposal_description(self, contract_address: str, proposal_id: int) -> str:
        """
        Attempt to fetch the description for a proposal.
        This is a placeholder - actual implementation would vary by governance contract.
        
        Args:
            contract_address: Address of the governance contract
            proposal_id: ID of the proposal
            
        Returns:
            Proposal description or a default message
        """
        # In a real implementation, you would query the contract or a subgraph
        # to get the proposal description
        return f"Proposal {proposal_id} from contract {contract_address}"


def get_context_fetcher() -> ContextFetcher:
    """
    Factory function to get the appropriate context fetcher based on configuration.
    
    Returns:
        ContextFetcher instance (either real or mock)
    """
    if USE_MOCK:
        # Import here to avoid circular imports
        from agent.mock_blockchain_client import MockBlockchainClient
        
        # Wrap the mock client in a context fetcher interface
        class MockContextFetcher(ContextFetcher):
            def __init__(self):
                self.mock_client = MockBlockchainClient()
            
            def get_recent_blocks(self, n: int = 128) -> List[Dict[str, Any]]:
                return self.mock_client.get_recent_blocks(n)
            
            def get_active_governor_proposals(self) -> List[Dict[str, Any]]:
                return self.mock_client.get_governance_proposals(active_only=True)
            
            def get_gas_price_stats(self, block_count: int = 100) -> Dict[str, Any]:
                gas_prices = self.mock_client.get_gas_prices(block_count)
                return {
                    "current_gas_price_gwei": 25.0,  # Mock value
                    "mean_base_fee_gwei": statistics.mean(gas_prices) if gas_prices else 25.0,
                    "median_base_fee_gwei": statistics.median(gas_prices) if gas_prices else 25.0,
                    "min_base_fee_gwei": min(gas_prices) if gas_prices else 20.0,
                    "max_base_fee_gwei": max(gas_prices) if gas_prices else 30.0,
                    "gas_prices": gas_prices,
                    "block_count": len(gas_prices),
                    "timestamp": int(time.time())
                }
        
        logger.info("Using mock context fetcher")
        return MockContextFetcher()
    else:
        # Use real Ethereum fetcher if Web3 is available
        if WEB3_AVAILABLE:
            logger.info("Using Ethereum context fetcher")
            return EthereumContextFetcher()
        else:
            # Fall back to mock if Web3 is not available
            logger.warning("Web3 not available, falling back to mock context fetcher")
            # Import here to avoid circular imports
            from agent.mock_blockchain_client import MockBlockchainClient
            return MockContextFetcher() 