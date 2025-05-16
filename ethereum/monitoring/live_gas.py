"""
Live Gas Metrics Collector

This module provides functionality to collect gas metrics from
a live Ethereum network using JSON-RPC calls.
"""

import os
import time
import json
import logging
import sqlite3
import statistics
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

import httpx

# Configure logging
logger = logging.getLogger("chaoschain.ethereum.live_gas")

# Default values
DEFAULT_RPC_URL = "https://sepolia.drpc.org"
DEFAULT_BLOCK_COUNT = 100
CACHE_DB_PATH = os.path.join(os.path.dirname(__file__), "../cache.db")


class LiveGasCollector:
    """
    Collector for Ethereum gas metrics from a live network.
    
    This class connects to an Ethereum JSON-RPC endpoint and collects
    gas usage statistics, fee history, and other metrics.
    """
    
    def __init__(
        self, 
        rpc_url: Optional[str] = None, 
        block_count: int = DEFAULT_BLOCK_COUNT,
        use_cache: bool = True
    ):
        """
        Initialize the live gas collector.
        
        Args:
            rpc_url: Ethereum JSON-RPC endpoint URL (defaults to DEFAULT_RPC_URL or ETH_RPC_URL env var)
            block_count: Number of blocks to analyze
            use_cache: Whether to use SQLite cache for block data
        """
        self.rpc_url = rpc_url or os.environ.get("ETH_RPC_URL", DEFAULT_RPC_URL)
        self.block_count = block_count
        self.use_cache = use_cache
        self.http_client = httpx.Client(timeout=30.0)
        
        logger.info(f"Initialized live gas collector with RPC URL: {self.rpc_url}")
        
        # Initialize the cache if needed
        if self.use_cache:
            self._init_cache()
    
    def _init_cache(self):
        """Initialize the SQLite cache database."""
        os.makedirs(os.path.dirname(CACHE_DB_PATH), exist_ok=True)
        
        conn = sqlite3.connect(CACHE_DB_PATH)
        cursor = conn.cursor()
        
        # Create blocks table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS blocks (
            number INTEGER PRIMARY KEY,
            timestamp INTEGER,
            hash TEXT,
            parentHash TEXT,
            gasLimit INTEGER,
            gasUsed INTEGER,
            baseFeePerGas INTEGER,
            data TEXT,
            fetched_at INTEGER
        )
        ''')
        
        # Create fee history table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS fee_history (
            block_range TEXT PRIMARY KEY,
            data TEXT,
            fetched_at INTEGER
        )
        ''')
        
        conn.commit()
        conn.close()
        
        logger.info(f"Initialized cache database at {CACHE_DB_PATH}")
    
    def _rpc_call(self, method: str, params: List[Any]) -> Dict[str, Any]:
        """
        Make an Ethereum JSON-RPC call.
        
        Args:
            method: RPC method name
            params: List of parameters for the method
            
        Returns:
            The 'result' field from the RPC response
            
        Raises:
            Exception: If the RPC call fails
        """
        payload = {
            "jsonrpc": "2.0",
            "id": int(time.time() * 1000),
            "method": method,
            "params": params
        }
        
        try:
            response = self.http_client.post(
                self.rpc_url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            
            result = response.json()
            if "error" in result:
                raise Exception(f"RPC error: {result['error']}")
            
            return result.get("result")
        except Exception as e:
            logger.error(f"RPC call failed: {e}")
            raise
    
    def _get_block_from_cache(self, block_number: int) -> Optional[Dict[str, Any]]:
        """
        Get a block from the cache if available.
        
        Args:
            block_number: The block number to retrieve
            
        Returns:
            The block data or None if not in cache
        """
        if not self.use_cache:
            return None
            
        conn = sqlite3.connect(CACHE_DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT data FROM blocks WHERE number = ?", 
            (block_number,)
        )
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return json.loads(result[0])
        
        return None
    
    def _store_block_in_cache(self, block: Dict[str, Any]):
        """
        Store a block in the cache.
        
        Args:
            block: The block data to store
        """
        if not self.use_cache:
            return
            
        conn = sqlite3.connect(CACHE_DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute(
            """
            INSERT OR REPLACE INTO blocks 
            (number, timestamp, hash, parentHash, gasLimit, gasUsed, baseFeePerGas, data, fetched_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                int(block["number"], 16) if isinstance(block["number"], str) else block["number"],
                int(block["timestamp"], 16) if isinstance(block["timestamp"], str) else block["timestamp"],
                block["hash"],
                block["parentHash"],
                int(block["gasLimit"], 16) if isinstance(block["gasLimit"], str) else block["gasLimit"],
                int(block["gasUsed"], 16) if isinstance(block["gasUsed"], str) else block["gasUsed"],
                int(block["baseFeePerGas"], 16) if isinstance(block["baseFeePerGas"], str) else block.get("baseFeePerGas", 0),
                json.dumps(block),
                int(time.time())
            )
        )
        
        conn.commit()
        conn.close()
    
    def _get_fee_history_from_cache(self, start_block: int, block_count: int) -> Optional[Dict[str, Any]]:
        """
        Get fee history from the cache if available.
        
        Args:
            start_block: Starting block number
            block_count: Number of blocks
            
        Returns:
            Fee history data or None if not in cache
        """
        if not self.use_cache:
            return None
            
        cache_key = f"{start_block}_{block_count}"
        
        conn = sqlite3.connect(CACHE_DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT data FROM fee_history WHERE block_range = ?", 
            (cache_key,)
        )
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return json.loads(result[0])
        
        return None
    
    def _store_fee_history_in_cache(self, start_block: int, block_count: int, data: Dict[str, Any]):
        """
        Store fee history in the cache.
        
        Args:
            start_block: Starting block number
            block_count: Number of blocks
            data: The fee history data to store
        """
        if not self.use_cache:
            return
            
        cache_key = f"{start_block}_{block_count}"
        
        conn = sqlite3.connect(CACHE_DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute(
            """
            INSERT OR REPLACE INTO fee_history 
            (block_range, data, fetched_at)
            VALUES (?, ?, ?)
            """,
            (
                cache_key,
                json.dumps(data),
                int(time.time())
            )
        )
        
        conn.commit()
        conn.close()
    
    def get_latest_block_number(self) -> int:
        """
        Get the latest block number from the network.
        
        Returns:
            The latest block number (as an integer)
        """
        try:
            result = self._rpc_call("eth_blockNumber", [])
            return int(result, 16)
        except Exception as e:
            logger.error(f"Failed to get latest block number: {e}")
            raise
    
    def get_block(self, block_number: int) -> Dict[str, Any]:
        """
        Get a block by number with full transaction details.
        
        Args:
            block_number: The block number to retrieve
            
        Returns:
            The block data including transactions
        """
        # Check cache first
        cached_block = self._get_block_from_cache(block_number)
        if cached_block:
            logger.debug(f"Block {block_number} found in cache")
            return cached_block
        
        # Convert to hex for RPC call
        block_hex = hex(block_number)
        
        try:
            block = self._rpc_call("eth_getBlockByNumber", [block_hex, True])
            
            # Store in cache
            self._store_block_in_cache(block)
            
            return block
        except Exception as e:
            logger.error(f"Failed to get block {block_number}: {e}")
            raise
    
    def get_fee_history(self, block_count: int, newest_block: int) -> Dict[str, Any]:
        """
        Get fee history for a range of blocks.
        
        Args:
            block_count: Number of blocks to retrieve
            newest_block: The newest block in the range
            
        Returns:
            Fee history data
        """
        # Check cache first
        cached_history = self._get_fee_history_from_cache(newest_block - block_count + 1, block_count)
        if cached_history:
            logger.debug(f"Fee history for blocks {newest_block-block_count+1}-{newest_block} found in cache")
            return cached_history
        
        try:
            fee_history = self._rpc_call("eth_feeHistory", [
                hex(block_count),
                hex(newest_block),
                [25, 50, 75]  # Percentiles
            ])
            
            # Store in cache
            self._store_fee_history_in_cache(newest_block - block_count + 1, block_count, fee_history)
            
            return fee_history
        except Exception as e:
            logger.error(f"Failed to get fee history: {e}")
            raise
    
    def collect_gas_metrics(self) -> Dict[str, Any]:
        """
        Collect comprehensive gas metrics from the network.
        
        Returns:
            Dict containing gas metrics data in the same format as the mock data
        """
        try:
            logger.info(f"Collecting gas metrics from {self.rpc_url}")
            
            # Get latest block number
            latest_block = self.get_latest_block_number()
            start_block = latest_block - self.block_count + 1
            
            logger.info(f"Analyzing blocks {start_block} to {latest_block}")
            
            # Collect blocks and transactions
            blocks_data = []
            gas_used_ratios = []
            base_fees = []
            
            for block_num in range(start_block, latest_block + 1):
                block = self.get_block(block_num)
                
                # Convert hex values to integers
                block_number = int(block["number"], 16) if isinstance(block["number"], str) else block["number"]
                gas_limit = int(block["gasLimit"], 16) if isinstance(block["gasLimit"], str) else block["gasLimit"]
                gas_used = int(block["gasUsed"], 16) if isinstance(block["gasUsed"], str) else block["gasUsed"]
                base_fee = int(block["baseFeePerGas"], 16) if isinstance(block["baseFeePerGas"], str) else block.get("baseFeePerGas", 0)
                timestamp = int(block["timestamp"], 16) if isinstance(block["timestamp"], str) else block["timestamp"]
                
                # Calculate gas used ratio
                gas_used_ratio = gas_used / gas_limit if gas_limit > 0 else 0
                gas_used_ratios.append(gas_used_ratio)
                
                # Add base fee to the list (in gwei)
                base_fee_gwei = base_fee / 1e9
                base_fees.append(base_fee_gwei)
                
                # Process transactions
                transactions = []
                for tx in block.get("transactions", []):
                    if isinstance(tx, dict):  # We requested full transaction objects
                        tx_gas_used = int(tx.get("gas", "0x0"), 16) if isinstance(tx.get("gas"), str) else tx.get("gas", 0)
                        tx_gas_price = int(tx.get("gasPrice", "0x0"), 16) if isinstance(tx.get("gasPrice"), str) else tx.get("gasPrice", 0)
                        
                        # Optional EIP-1559 fields
                        max_priority_fee = int(tx.get("maxPriorityFeePerGas", "0x0"), 16) if isinstance(tx.get("maxPriorityFeePerGas"), str) else tx.get("maxPriorityFeePerGas", 0)
                        max_fee = int(tx.get("maxFeePerGas", "0x0"), 16) if isinstance(tx.get("maxFeePerGas"), str) else tx.get("maxFeePerGas", 0)
                        
                        transactions.append({
                            "hash": tx.get("hash"),
                            "gasUsed": tx_gas_used,
                            "gasPrice": tx_gas_price / 1e9,  # Convert to gwei
                            "maxPriorityFeePerGas": max_priority_fee / 1e9 if max_priority_fee else None,
                            "maxFeePerGas": max_fee / 1e9 if max_fee else None
                        })
                
                blocks_data.append({
                    "number": block_number,
                    "timestamp": timestamp,
                    "gasLimit": gas_limit,
                    "gasUsed": gas_used,
                    "gasUsedRatio": gas_used_ratio,
                    "baseFeePerGas": base_fee_gwei,
                    "transactions": transactions
                })
            
            # Calculate statistics
            avg_gas_used_ratio = statistics.mean(gas_used_ratios) if gas_used_ratios else 0
            avg_base_fee = statistics.mean(base_fees) if base_fees else 0
            base_fee_volatility = statistics.stdev(base_fees) / avg_base_fee if base_fees and avg_base_fee > 0 else 0
            
            # Collect network metrics
            network_metrics = {
                "avgBlockTime": self._calculate_avg_block_time(blocks_data),
                "avgGasPrice": avg_base_fee + 2,  # Approximation: base fee + 2 gwei priority fee
                "pendingTxCount": self._get_pending_tx_count(),
                "peerCount": self._get_peer_count()
            }
            
            # Get fee history for more detailed fee metrics
            fee_history = self.get_fee_history(min(100, self.block_count), latest_block)
            
            # Construct the metrics result in the same format as the mock data
            result = {
                "timestamp": datetime.now().isoformat(),
                "blocks": blocks_data,
                "network": network_metrics,
                "statistics": {
                    "avgGasUsedRatio": avg_gas_used_ratio,
                    "avgBaseFee": avg_base_fee,
                    "baseFeeVolatility": base_fee_volatility,
                    "blockRange": {
                        "start": start_block,
                        "end": latest_block
                    }
                }
            }
            
            logger.info(f"Successfully collected gas metrics: {len(blocks_data)} blocks analyzed")
            return result
            
        except Exception as e:
            logger.error(f"Failed to collect gas metrics: {e}")
            # If we can't get live data, return None and let the caller
            # decide whether to fall back to mock data
            return None
    
    def _calculate_avg_block_time(self, blocks: List[Dict[str, Any]]) -> float:
        """
        Calculate average block time from block data.
        
        Args:
            blocks: List of block data
            
        Returns:
            Average block time in seconds
        """
        if len(blocks) < 2:
            return 12.0  # Default value
        
        # Sort blocks by number to ensure correct order
        sorted_blocks = sorted(blocks, key=lambda b: b["number"])
        
        # Calculate time differences
        time_diffs = []
        for i in range(1, len(sorted_blocks)):
            time_diff = sorted_blocks[i]["timestamp"] - sorted_blocks[i-1]["timestamp"]
            if time_diff > 0:  # Skip negative differences (can happen with out-of-order blocks)
                time_diffs.append(time_diff)
        
        return statistics.mean(time_diffs) if time_diffs else 12.0
    
    def _get_pending_tx_count(self) -> int:
        """
        Get the number of pending transactions.
        
        Returns:
            Number of pending transactions
        """
        try:
            result = self._rpc_call("eth_getBlockTransactionCountByNumber", ["pending"])
            return int(result, 16) if result else 0
        except Exception as e:
            logger.warning(f"Failed to get pending transaction count: {e}")
            return 0
    
    def _get_peer_count(self) -> int:
        """
        Get the number of peers connected to the node.
        
        Returns:
            Number of peers
        """
        try:
            result = self._rpc_call("net_peerCount", [])
            return int(result, 16) if result else 0
        except Exception as e:
            logger.warning(f"Failed to get peer count: {e}")
            return 0


def get_gas_metrics(use_cache: bool = True, rpc_url: Optional[str] = None) -> Dict[str, Any]:
    """
    Get gas metrics from live Ethereum network.
    
    This is the main function to call from other modules.
    
    Args:
        use_cache: Whether to use SQLite cache
        rpc_url: Ethereum JSON-RPC endpoint URL
        
    Returns:
        Dict containing gas metrics data
    """
    collector = LiveGasCollector(rpc_url=rpc_url, use_cache=use_cache)
    return collector.collect_gas_metrics()


if __name__ == "__main__":
    # Enable logging when run directly
    logging.basicConfig(level=logging.INFO)
    
    # Simple example usage
    metrics = get_gas_metrics()
    if metrics:
        print(f"Successfully collected gas metrics from {len(metrics['blocks'])} blocks")
        print(f"Average gas used ratio: {metrics['statistics']['avgGasUsedRatio']:.2f}")
        print(f"Average base fee: {metrics['statistics']['avgBaseFee']:.2f} gwei")
        print(f"Base fee volatility: {metrics['statistics']['baseFeeVolatility']:.2f}")
    else:
        print("Failed to collect gas metrics") 