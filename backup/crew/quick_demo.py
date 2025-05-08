#!/usr/bin/env python
"""
Simple CrewAI agent demo that connects to Sepolia,
fetches latest block metrics, and outputs a proposal.
"""

import argparse
import json
import os
from datetime import datetime
from typing import Dict, Any

import requests
from crewai import Agent, Crew, Task
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class EthereumRPCClient:
    """Simple Ethereum JSON-RPC client."""
    
    def __init__(self, rpc_url: str):
        """Initialize with RPC URL."""
        self.rpc_url = rpc_url
        self.request_id = 1
    
    def _call(self, method: str, params: list = None) -> Dict[str, Any]:
        """Make a JSON-RPC call."""
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or [],
            "id": self.request_id
        }
        self.request_id += 1
        
        response = requests.post(self.rpc_url, json=payload)
        response.raise_for_status()
        result = response.json()
        
        if "error" in result:
            raise Exception(f"RPC error: {result['error']}")
        
        return result["result"]
    
    def get_latest_block_number(self) -> int:
        """Get the latest block number."""
        return int(self._call("eth_blockNumber"), 16)
    
    def get_block_by_number(self, block_number: int = None, full_tx: bool = False) -> Dict[str, Any]:
        """Get block details by number."""
        block_param = "latest" if block_number is None else hex(block_number)
        return self._call("eth_getBlockByNumber", [block_param, full_tx])
    
    def get_gas_price(self) -> int:
        """Get current gas price in wei."""
        return int(self._call("eth_gasPrice"), 16)


def create_ethereum_chain_monitor(rpc_url: str) -> Agent:
    """Create an agent for monitoring Ethereum chain."""
    return Agent(
        role="Ethereum Chain Analyzer",
        goal="Monitor Ethereum chain metrics and identify potential parameter optimizations",
        backstory="""You are an expert in Ethereum blockchain analysis. 
        Your job is to monitor key metrics and suggest parameter optimizations
        based on network activity.""",
        tools=[],
        verbose=True
    )


def create_proposal_generator() -> Agent:
    """Create an agent for generating parameter adjustment proposals."""
    return Agent(
        role="Governance Proposal Generator",
        goal="Generate parameter adjustment proposals based on chain analysis",
        backstory="""You are a blockchain governance expert. You take analysis
        of chain metrics and convert them into concrete parameter adjustment
        proposals to optimize the network.""",
        tools=[],
        verbose=True
    )


def main():
    """Main function to run the CrewAI demo."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="CrewAI Ethereum chain monitor demo")
    parser.add_argument("--rpc", required=True, help="Ethereum RPC URL")
    args = parser.parse_args()
    
    # Initialize Ethereum RPC client
    client = EthereumRPCClient(args.rpc)
    
    try:
        # Fetch chain metrics
        block_number = client.get_latest_block_number()
        block_data = client.get_block_by_number(block_number)
        gas_price = client.get_gas_price()
        
        # Format the metrics
        gas_used = int(block_data["gasUsed"], 16)
        gas_limit = int(block_data["gasLimit"], 16)
        utilization = gas_used / gas_limit * 100
        
        metrics = {
            "block_number": block_number,
            "timestamp": datetime.now().isoformat(),
            "gas_price_gwei": gas_price / 1e9,
            "gas_used": gas_used,
            "gas_limit": gas_limit,
            "utilization_percentage": utilization
        }
        
        print("Chain Metrics:")
        print(json.dumps(metrics, indent=2))
        
        # Create CrewAI agents
        analyzer = create_ethereum_chain_monitor(args.rpc)
        generator = create_proposal_generator()
        
        # Create tasks
        analyze_task = Task(
            description=f"""
            Analyze the following Ethereum metrics and identify potential parameter optimizations:
            Block Number: {block_number}
            Gas Used: {gas_used}
            Gas Limit: {gas_limit}
            Gas Utilization: {utilization:.2f}%
            Gas Price: {gas_price / 1e9:.2f} Gwei
            """,
            agent=analyzer
        )
        
        generate_task = Task(
            description="""
            Based on the analysis, generate a parameter adjustment proposal.
            Focus on gas limit adjustment to optimize for throughput while maintaining stability.
            """,
            agent=generator,
            context=[analyze_task]
        )
        
        # Create and run the crew
        crew = Crew(
            agents=[analyzer, generator],
            tasks=[analyze_task, generate_task],
            verbose=True
        )
        
        result = crew.kickoff()
        
        # Format the result as a proposal
        proposal = {
            "type": "ParameterAdjustment",
            "chain": "Sepolia",
            "metrics": metrics,
            "analysis": result,
            "proposed_changes": {
                "parameter": "gasLimit",
                "current_value": gas_limit,
                "proposed_value": int(gas_limit * 1.05),  # Example: 5% increase
                "justification": "Increase gas limit to improve throughput based on current utilization",
            },
            "timestamp": datetime.now().isoformat()
        }
        
        print("\nGenerated Proposal:")
        print(json.dumps(proposal, indent=2))
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main()) 