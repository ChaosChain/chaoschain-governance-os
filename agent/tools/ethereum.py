"""
Ethereum Tools

This module provides tools for interacting with Ethereum nodes and analyzing blockchain data.
"""

import os
import json
import statistics
from typing import Dict, List, Any, Optional, Type
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from web3 import Web3
import requests

class GasMetricsTool(BaseTool):
    """Tool for retrieving and analyzing Ethereum gas metrics."""
    
    name: str = "gas_metrics_analyzer"
    description: str = """
    Analyze Ethereum gas metrics over a range of blocks.
    Returns statistics about gas usage, including average gas price, gas used ratio,
    and base fee trends. Use this to identify potential gas parameter optimization opportunities.
    """
    
    def _get_web3(self) -> Web3:
        """Get Web3 instance using environment variables."""
        rpc_url = os.getenv("ETHEREUM_RPC_URL")
        if not rpc_url:
            raise ValueError("ETHEREUM_RPC_URL environment variable not set")
        return Web3(Web3.HTTPProvider(rpc_url))
    
    def _run(self, block_range: str = "latest-100:latest") -> str:
        """
        Analyze gas metrics over a range of blocks.
        
        Args:
            block_range: Range of blocks to analyze (e.g., "latest-100:latest" or "17000000:17000100")
            
        Returns:
            JSON string with gas metrics analysis
        """
        w3 = self._get_web3()
        
        # Parse block range
        if block_range == "latest-100:latest":
            latest_block = w3.eth.block_number
            start_block = latest_block - 100
            end_block = latest_block
        else:
            parts = block_range.split(":")
            if len(parts) != 2:
                return json.dumps({"error": "Invalid block range format. Use 'start:end'"})
            start_block = int(parts[0])
            end_block = int(parts[1])
        
        # Collect gas data
        gas_prices = []
        gas_used_ratios = []
        base_fees = []
        
        for block_num in range(start_block, end_block + 1):
            try:
                block = w3.eth.get_block(block_num, full_transactions=False)
                if hasattr(block, 'baseFeePerGas'):
                    base_fee = block.baseFeePerGas / 1e9  # Convert to Gwei
                    base_fees.append(base_fee)
                
                gas_limit = block.gasLimit
                gas_used = block.gasUsed
                gas_used_ratio = gas_used / gas_limit
                gas_used_ratios.append(gas_used_ratio)
                
                # For pre-London blocks, estimate gas price from transactions
                if not hasattr(block, 'baseFeePerGas'):
                    # This is simplified, in a real implementation we'd analyze actual txs
                    gas_price = w3.eth.gas_price / 1e9  # Convert to Gwei
                    gas_prices.append(gas_price)
            except Exception as e:
                continue
        
        # Calculate statistics
        metrics = {
            "block_range": f"{start_block}:{end_block}",
            "blocks_analyzed": len(gas_used_ratios),
            "gas_used_ratio": {
                "mean": statistics.mean(gas_used_ratios) if gas_used_ratios else None,
                "median": statistics.median(gas_used_ratios) if gas_used_ratios else None,
                "min": min(gas_used_ratios) if gas_used_ratios else None,
                "max": max(gas_used_ratios) if gas_used_ratios else None,
            }
        }
        
        if base_fees:
            metrics["base_fee_gwei"] = {
                "mean": statistics.mean(base_fees),
                "median": statistics.median(base_fees),
                "min": min(base_fees),
                "max": max(base_fees),
                "trend": "increasing" if base_fees[-1] > base_fees[0] else "decreasing"
            }
        
        if gas_prices:
            metrics["gas_price_gwei"] = {
                "mean": statistics.mean(gas_prices),
                "median": statistics.median(gas_prices),
                "min": min(gas_prices),
                "max": max(gas_prices)
            }
        
        # Analyze the results for optimization opportunities
        analysis = self._analyze_metrics(metrics)
        metrics["analysis"] = analysis
        
        return json.dumps(metrics, indent=2)
    
    def _analyze_metrics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze metrics to identify potential optimization opportunities.
        
        Args:
            metrics: Dictionary of gas metrics
            
        Returns:
            Dictionary with analysis results
        """
        analysis = {
            "findings": [],
            "recommendations": []
        }
        
        # Gas used ratio analysis
        if metrics["gas_used_ratio"]["mean"] is not None:
            mean_ratio = metrics["gas_used_ratio"]["mean"]
            if mean_ratio > 0.9:
                analysis["findings"].append("Gas usage consistently high (>90% of limit)")
                analysis["recommendations"].append("Consider increasing gas limit to reduce competition")
            elif mean_ratio < 0.3:
                analysis["findings"].append("Gas usage consistently low (<30% of limit)")
                analysis["recommendations"].append("Consider reducing gas limit to optimize block space")
        
        # Base fee analysis
        if "base_fee_gwei" in metrics:
            base_fee = metrics["base_fee_gwei"]
            if base_fee["max"] / base_fee["min"] > 5:
                analysis["findings"].append("High base fee volatility (max/min > 5x)")
                analysis["recommendations"].append(
                    "Consider adjusting EIP-1559 parameters to smooth fee changes"
                )
        
        return analysis


class BlockDataTool(BaseTool):
    """Tool for retrieving detailed data from specific Ethereum blocks."""
    
    name: str = "ethereum_block_data"
    description: str = """
    Retrieve detailed data from specific Ethereum blocks.
    Returns block information including timestamp, transactions count, gas used, gas limit,
    and other block metrics. Use this to examine specific blocks in detail.
    """
    
    def _get_web3(self) -> Web3:
        """Get Web3 instance using environment variables."""
        rpc_url = os.getenv("ETHEREUM_RPC_URL")
        if not rpc_url:
            raise ValueError("ETHEREUM_RPC_URL environment variable not set")
        return Web3(Web3.HTTPProvider(rpc_url))
    
    def _run(self, block_identifier: str = "latest") -> str:
        """
        Get detailed data for a specific Ethereum block.
        
        Args:
            block_identifier: Block number or "latest"
            
        Returns:
            JSON string with block data
        """
        w3 = self._get_web3()
        
        try:
            # Convert to int if it's a number, otherwise use as is
            if block_identifier != "latest" and block_identifier.isdigit():
                block_identifier = int(block_identifier)
                
            block = w3.eth.get_block(block_identifier, full_transactions=False)
            
            # Convert to dictionary and handle non-serializable types
            block_dict = dict(block)
            for key, value in block_dict.items():
                if isinstance(value, (bytes, bytearray)):
                    block_dict[key] = value.hex()
                elif hasattr(value, "hex"):
                    block_dict[key] = value.hex()
                elif isinstance(value, int) and key in ["timestamp"]:
                    # Keep timestamp as int
                    continue
                elif isinstance(value, int):
                    # Convert other large ints to strings to avoid JSON serialization issues
                    block_dict[key] = str(value)
            
            # Add some computed fields
            if "gasUsed" in block_dict and "gasLimit" in block_dict:
                gas_used = int(block_dict["gasUsed"], 16) if isinstance(block_dict["gasUsed"], str) else int(block_dict["gasUsed"])
                gas_limit = int(block_dict["gasLimit"], 16) if isinstance(block_dict["gasLimit"], str) else int(block_dict["gasLimit"])
                block_dict["gasUsedRatio"] = gas_used / gas_limit
            
            return json.dumps(block_dict, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)}) 