#!/usr/bin/env python3
"""
ChaosCore SDK Gateway Demo

This script demonstrates the ChaosCore API Gateway with SGX enclaves and Ethereum anchoring.
"""

import os
import sys
import time
import argparse
import json
import requests
from typing import Dict, Any, Optional, List
import logging
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import the client from the API Gateway
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api_gateway.client_example import ChaosCorePlatformClient

# Ethereum configuration
ETHEREUM_NETWORK = "goerli"
ETHEREUM_RPC_URL = os.environ.get("ETHEREUM_RPC_URL", "https://goerli.infura.io/v3/your-project-id")
ETHEREUM_WALLET_KEY = os.environ.get("ETHEREUM_WALLET_KEY", None)

# SGX Enclave configuration
SGX_ENCLAVE_URL = os.environ.get("SGX_ENCLAVE_URL", "http://localhost:7000")

class DemoRunner:
    """
    Runner for the SDK Gateway demo.
    """
    
    def __init__(self, api_url: str = "http://localhost:8000", use_staging: bool = False, anchor_eth: bool = False):
        """
        Initialize the demo runner.
        
        Args:
            api_url: URL of the API Gateway
            use_staging: Whether to use staging environment
            anchor_eth: Whether to anchor to Ethereum
        """
        self.api_url = api_url
        self.use_staging = use_staging
        self.anchor_eth = anchor_eth
        self.client = ChaosCorePlatformClient(base_url=api_url)
        self.token = None
        self.agent_id = None
        self.studio_id = None
        self.actions = []
        
        logger.info(f"Demo runner initialized with API URL: {api_url}")
        logger.info(f"Staging mode: {use_staging}")
        logger.info(f"Ethereum anchoring: {anchor_eth}")
    
    def check_sgx_enclave(self) -> Dict[str, Any]:
        """
        Check SGX enclave status.
        
        Returns:
            Dict[str, Any]: Enclave info
        """
        logger.info(f"Checking SGX enclave at {SGX_ENCLAVE_URL}")
        try:
            response = requests.get(f"{SGX_ENCLAVE_URL}/info")
            response.raise_for_status()
            enclave_info = response.json()
            logger.info(f"SGX enclave info: {json.dumps(enclave_info, indent=2)}")
            return enclave_info
        except Exception as e:
            logger.error(f"Failed to check SGX enclave: {e}")
            logger.warning("Continuing without SGX enclave verification")
            return {"status": "unavailable", "error": str(e)}
    
    def register_agent(self) -> str:
        """
        Register a demo agent.
        
        Returns:
            str: Agent ID
        """
        logger.info("Registering demo agent")
        agent = self.client.register_agent(
            name="Demo Agent",
            email=f"demo-{uuid.uuid4()}@example.com",
            metadata={
                "role": "Demo",
                "expertise": "API Gateway Testing",
                "version": "1.0.0"
            }
        )
        
        self.agent_id = agent["agent_id"]
        logger.info(f"Agent registered with ID: {self.agent_id}")
        return self.agent_id
    
    def create_studio(self) -> str:
        """
        Create a demo studio.
        
        Returns:
            str: Studio ID
        """
        logger.info("Creating demo studio")
        studio = self.client.create_studio(
            name="Demo Studio",
            description="Studio for testing the API Gateway",
            metadata={
                "domain": "testing",
                "version": "1.0.0",
                "tags": ["demo", "test", "api"]
            }
        )
        
        self.studio_id = studio["id"]
        logger.info(f"Studio created with ID: {self.studio_id}")
        return self.studio_id
    
    def execute_simulation(self) -> str:
        """
        Execute a simulation action.
        
        Returns:
            str: Action ID
        """
        logger.info("Executing simulation")
        action = self.client.log_action(
            action_type="SIMULATE",
            description="Simulating blockchain parameters",
            data={
                "chain": "ethereum",
                "network": ETHEREUM_NETWORK,
                "parameters": {
                    "gas_limit": 15000000,
                    "gas_target": 10000000,
                    "base_fee": 10,
                    "priority_fee": 2
                }
            }
        )
        
        action_id = action["id"]
        self.actions.append(action_id)
        logger.info(f"Simulation action logged with ID: {action_id}")
        
        # Record outcome after simulation is "complete"
        time.sleep(1)  # Simulate some processing time
        
        outcome = self.client.record_outcome(
            action_id=action_id,
            success=True,
            results={
                "optimized_params": {
                    "gas_limit": 12500000,
                    "gas_target": 8000000,
                    "base_fee": 8,
                    "priority_fee": 1
                },
                "improvement": "25%",
                "confidence": 0.92
            },
            impact_score=0.85
        )
        
        logger.info(f"Simulation outcome recorded with success: {outcome['success']}")
        return action_id
    
    def anchor_to_ethereum(self, action_id: str) -> Optional[str]:
        """
        Anchor an action to Ethereum.
        
        Args:
            action_id: Action ID to anchor
            
        Returns:
            Optional[str]: Transaction hash if successful
        """
        if not self.anchor_eth:
            logger.info("Ethereum anchoring disabled, skipping")
            return None
        
        if not ETHEREUM_WALLET_KEY:
            logger.warning("No Ethereum wallet key provided, using mock anchoring")
            tx_hash = f"0x{uuid.uuid4().hex}"
            logger.info(f"Mock transaction hash: {tx_hash}")
            return tx_hash
        
        logger.info(f"Anchoring action {action_id} to Ethereum {ETHEREUM_NETWORK}")
        
        # In a real implementation, we would use web3.py to submit a transaction
        # For this demo, we'll just generate a mock transaction hash
        tx_hash = f"0x{uuid.uuid4().hex}"
        logger.info(f"Transaction hash: {tx_hash}")
        
        return tx_hash
    
    def check_reputation(self) -> float:
        """
        Check agent reputation.
        
        Returns:
            float: Reputation score
        """
        logger.info(f"Checking reputation for agent {self.agent_id}")
        reputation = self.client.get_agent_reputation(self.agent_id)
        
        score = reputation["score"]
        logger.info(f"Agent reputation score: {score}")
        
        return score
    
    def run(self):
        """
        Run the demo.
        """
        logger.info("Starting ChaosCore SDK Gateway Demo")
        
        # Check SGX enclave
        enclave_info = self.check_sgx_enclave()
        enclave_hash = enclave_info.get("enclave_hash", "unknown")
        print(f"Enclave hash: {enclave_hash}")
        
        # Register agent
        self.register_agent()
        
        # Create studio
        self.create_studio()
        
        # Execute simulation
        action_id = self.execute_simulation()
        
        # Anchor to Ethereum
        tx_hash = self.anchor_to_ethereum(action_id)
        if tx_hash:
            print(f"Goerli tx hash: {tx_hash}")
        
        # Check reputation
        initial_reputation = self.check_reputation()
        
        # Create a task in the studio
        task = self.client.create_task(
            studio_id=self.studio_id,
            name="Implement Gas Optimization",
            description="Implement the optimized gas parameters from simulation",
            parameters={
                "priority": "high",
                "deadline": "2023-12-31",
                "team_size": 3
            }
        )
        
        logger.info(f"Task created with ID: {task['id']}")
        
        # Log implementation action
        implementation_action = self.client.log_action(
            action_type="IMPLEMENT",
            description="Implementing optimized gas parameters",
            data={
                "task_id": task["id"],
                "chain": "ethereum",
                "network": ETHEREUM_NETWORK,
                "parameters": {
                    "gas_limit": 12500000,
                    "gas_target": 8000000,
                    "base_fee": 8,
                    "priority_fee": 1
                }
            }
        )
        
        action_id = implementation_action["id"]
        self.actions.append(action_id)
        logger.info(f"Implementation action logged with ID: {action_id}")
        
        # Record outcome after implementation is "complete"
        time.sleep(1)  # Simulate some processing time
        
        outcome = self.client.record_outcome(
            action_id=action_id,
            success=True,
            results={
                "deployed": True,
                "transaction_hash": f"0x{uuid.uuid4().hex}",
                "gas_saved": "28%",
                "validation_score": 0.95
            },
            impact_score=0.9
        )
        
        logger.info(f"Implementation outcome recorded with success: {outcome['success']}")
        
        # Check updated reputation
        final_reputation = self.check_reputation()
        reputation_delta = final_reputation - initial_reputation
        print(f"Reputation delta: {reputation_delta:.4f}")
        
        logger.info("Demo completed successfully")


def main():
    """
    Main entry point.
    """
    parser = argparse.ArgumentParser(description="ChaosCore SDK Gateway Demo")
    parser.add_argument("--url", default="http://localhost:8000", help="API Gateway URL")
    parser.add_argument("--stage", action="store_true", help="Use staging environment")
    parser.add_argument("--anchor-eth", action="store_true", help="Anchor to Ethereum")
    
    args = parser.parse_args()
    
    # Run the demo
    runner = DemoRunner(api_url=args.url, use_staging=args.stage, anchor_eth=args.anchor_eth)
    runner.run()


if __name__ == "__main__":
    main() 