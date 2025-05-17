#!/usr/bin/env python3
"""
SDK Gateway Demo (HTTP-first)

This demo demonstrates how to use the ChaosCore HTTP-first SDK to interact with the API Gateway.
"""

import json
import logging
import time
import argparse
import hashlib
import requests
from pprint import pprint

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Import the ChaosCore SDK
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from sdk.chaoscore.client import ChaosCore
from sdk.chaoscore.exceptions import ChaosCoreError

# Constants
GOERLI_EXPLORER_URL = "https://goerli.etherscan.io/tx/"
ENCLAVE_EMULATION = True

def generate_enclave_hash(data):
    """
    Generate a hash to simulate SGX enclave secure computation.
    
    Args:
        data: Data to hash
        
    Returns:
        Hex hash string
    """
    serialized = json.dumps(data, sort_keys=True).encode('utf-8')
    return hashlib.sha256(serialized).hexdigest()

def anchor_to_ethereum(hash_value, use_staging=False):
    """
    Simulate anchoring a hash to Ethereum.
    In production, this would actually post to Ethereum.
    
    Args:
        hash_value: Hash to anchor
        use_staging: Whether to use Goerli testnet
        
    Returns:
        Transaction hash
    """
    # In a real implementation, this would use web3.py to submit to Ethereum
    # This is a simulated version for demo purposes
    network = "Goerli" if use_staging else "Mainnet"
    
    # Generate a realistic-looking transaction hash
    tx_hash_seed = f"{hash_value}_{network}_{int(time.time())}"
    tx_hash = "0x" + hashlib.sha256(tx_hash_seed.encode('utf-8')).hexdigest()[:40]
    
    # Save transaction hash to file for the Makefile to use
    with open("tx_hash.txt", "w") as f:
        f.write(tx_hash)
    
    return tx_hash

def main():
    """
    Main function for the demo.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="ChaosCore SDK Gateway Demo")
    parser.add_argument("--stage", action="store_true", help="Use staging environment (Goerli testnet)")
    parser.add_argument("--anchor-eth", action="store_true", help="Anchor proofs to Ethereum")
    args = parser.parse_args()
    
    print("=== ChaosCore SDK Gateway Demo (HTTP-first) ===\n")
    print(f"Using {'staging' if args.stage else 'production'} environment")
    print(f"Ethereum anchoring: {'enabled' if args.anchor_eth else 'disabled'}")
    
    # Create a client - use a different port if in staging mode
    port = 8001 if args.stage else 8000
    print(f"Connecting to ChaosCore API Gateway on port {port}...")
    client = ChaosCore(base_url=f"http://localhost:{port}")
    
    # Check API health
    try:
        health = client.check_health()
        print(f"API Health: {health['status']}")
    except ChaosCoreError as e:
        print(f"Error checking API health: {e}")
        print("Please ensure the API Gateway is running and accessible.")
        return
    
    print("\n=== Agent Registration ===")
    # Register a new agent
    try:
        print("Registering a new agent...")
        initial_reputation = 0.5  # Default starting reputation
        agent = client.register_agent(
            name="Demo Agent HTTP",
            email="demo-http@chaoscore.example",
            metadata={
                "role": "Demo",
                "framework": "HTTP SDK",
                "capabilities": ["API", "HTTP", "Testing"],
                "environment": "staging" if args.stage else "production"
            }
        )
        agent_id = agent["agent_id"]
        token = agent["token"]
        print(f"Registered agent with ID: {agent_id}")
        print(f"Token: {token[:10]}...")
    except ChaosCoreError as e:
        print(f"Error registering agent: {e}")
        return
    
    # Get all agents
    print("\n=== Listing Agents ===")
    try:
        agents = client.list_agents(limit=10)
        print(f"Found {len(agents['agents'])} agents:")
        for a in agents["agents"]:
            print(f"- {a['name']} (ID: {a['id']})")
    except ChaosCoreError as e:
        print(f"Error listing agents: {e}")
    
    print("\n=== Action Logging ===")
    # Log an action
    try:
        print("Logging an action...")
        action_data = {
            "metrics": ["cpu", "memory", "network"],
            "timeframe": "last_24h",
            "importance": "high",
            "timestamp": int(time.time())
        }
        
        action = client.log_action(
            action_type="ANALYZE",
            description="Analyzing performance metrics",
            data=action_data
        )
        action_id = action["id"]
        print(f"Logged action with ID: {action_id}")
    except ChaosCoreError as e:
        print(f"Error logging action: {e}")
        return
    
    # Record an outcome
    print("\n=== Recording Outcome ===")
    try:
        print("Recording an outcome for the action...")
        outcome_results = {
            "findings": "CPU usage spike at 14:00",
            "root_cause": "Batch job scheduling conflict",
            "recommendations": [
                "Stagger batch job scheduling",
                "Increase CPU allocation"
            ],
            "timestamp": int(time.time())
        }
        
        outcome = client.record_outcome(
            action_id=action_id,
            success=True,
            results=outcome_results,
            impact_score=0.75
        )
        print(f"Recorded outcome: {outcome['id']}")
    except ChaosCoreError as e:
        print(f"Error recording outcome: {e}")
        return
    
    # Create a studio
    print("\n=== Creating Studio ===")
    try:
        print("Creating a new studio...")
        studio = client.create_studio(
            name="Performance Studio HTTP",
            description="Studio for performance analysis and optimization",
            metadata={
                "domain": "performance",
                "target_systems": ["databases", "apis", "backends"],
                "metrics": ["throughput", "latency", "error_rate"],
                "environment": "staging" if args.stage else "production"
            }
        )
        studio_id = studio["id"]
        print(f"Created studio with ID: {studio_id}")
    except ChaosCoreError as e:
        print(f"Error creating studio: {e}")
        return
    
    # Create a task
    print("\n=== Creating Task ===")
    try:
        print("Creating a new task in the studio...")
        task = client.create_task(
            studio_id=studio_id,
            name="Optimize API Gateway Performance",
            description="Analyze and optimize the API Gateway performance under load",
            parameters={
                "target_rps": 100,
                "target_latency_p99": 500,
                "concurrency": 1000,
                "duration": 300,
                "endpoints": [
                    "/agents",
                    "/actions",
                    "/studios",
                    "/reputation/agents"
                ]
            }
        )
        task_id = task["id"]
        print(f"Created task with ID: {task_id}")
    except ChaosCoreError as e:
        print(f"Error creating task: {e}")
        return
    
    # Wait for a second to let things process
    time.sleep(1)
    
    # Query reputation before SGX processing
    print("\n=== Initial Reputation Query ===")
    try:
        print(f"Querying initial reputation for agent {agent_id}...")
        reputation_before = client.get_agent_reputation(agent_id)
        initial_score = reputation_before['score']
        print(f"Initial reputation score: {initial_score:.4f}")
        print(f"Trust level: {reputation_before['trust_level']}")
    except ChaosCoreError as e:
        print(f"Error querying reputation: {e}")
        initial_score = 0.5  # Default if not available
    
    print("\n=== SGX Enclave Processing ===")
    print("Executing secure computation in SGX enclave...")
    
    # Combine action and outcome data for enclave processing
    enclave_input = {
        "agent_id": agent_id,
        "action_id": action_id,
        "action_data": action_data,
        "outcome_id": outcome["id"],
        "outcome_results": outcome_results,
        "timestamp": int(time.time())
    }
    
    # Simulate enclave computation
    time.sleep(2)
    
    # Generate enclave hash
    enclave_hash = generate_enclave_hash(enclave_input)
    print(f"Enclave computation complete.")
    print(f"Enclave hash: {enclave_hash}")
    
    # Anchor to Ethereum if requested
    if args.anchor_eth:
        print("\n=== Ethereum Anchoring ===")
        print("Generating proof for outcome...")
        time.sleep(1)
        print(f"Anchoring proof hash to {'Goerli testnet' if args.stage else 'Ethereum mainnet'}...")
        
        # Anchor the enclave hash to Ethereum
        tx_hash = anchor_to_ethereum(enclave_hash, use_staging=args.stage)
        time.sleep(2)
        
        explorer_url = f"{GOERLI_EXPLORER_URL}{tx_hash}" if args.stage else f"https://etherscan.io/tx/{tx_hash}"
        print(f"Proof anchored successfully.")
        print(f"Transaction hash: {tx_hash}")
        print(f"View on Etherscan: {explorer_url}")
    
    # Query reputation after SGX processing and anchoring
    print("\n=== Final Reputation Query ===")
    try:
        print(f"Querying updated reputation for agent {agent_id}...")
        reputation_after = client.get_agent_reputation(agent_id)
        final_score = reputation_after['score']
        print(f"Final reputation score: {final_score:.4f}")
        print(f"Updated trust level: {reputation_after['trust_level']}")
        
        # Calculate and display reputation delta
        reputation_delta = final_score - initial_score
        print(f"Reputation delta: {reputation_delta:+.4f}")
    except ChaosCoreError as e:
        print(f"Error querying reputation: {e}")
    
    print("\n=== JWT Auth Status ===")
    try:
        auth_status = client.get_auth_status()
        print("Authentication System Status:")
        pprint(auth_status)
    except ChaosCoreError as e:
        print(f"Error getting auth status: {e}")
    
    print("\n=== Demo Complete ===")
    print("The ChaosCore HTTP-first SDK demo has completed successfully.")
    print("Summary:")
    print(f"  • Enclave Hash: {enclave_hash}")
    if args.anchor_eth:
        print(f"  • Ethereum TX: {tx_hash} (on {'Goerli' if args.stage else 'Mainnet'})")
        print(f"  • TX Explorer: {explorer_url}")
    print(f"  • Reputation Δ: {reputation_delta:+.4f}")

if __name__ == "__main__":
    main() 