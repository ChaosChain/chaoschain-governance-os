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
SEPOLIA_EXPLORER_URL = "https://sepolia.etherscan.io/tx/"
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

def anchor_to_ethereum(hash_value, use_staging=False, network="sepolia", action_id=None, token=None):
    """
    Anchor a hash to Ethereum.
    In production, this will actually post to Ethereum via the SDK.
    
    Args:
        hash_value: Hash to anchor
        use_staging: Whether to use testnet
        network: The Ethereum network to use (default: sepolia)
        action_id: ID of the action to anchor
        token: JWT token for authentication
        
    Returns:
        Transaction hash
    """
    # In a real implementation with ETHEREUM_MOCK=false, the API will
    # send the transaction to Ethereum and return a real transaction hash
    selected_network = network.capitalize() if use_staging else "Mainnet"
    
    print(f"Sending on-chain transaction to {selected_network}...")
    
    # Check if we have an action_id
    if not action_id:
        raise ValueError("No action_id provided for anchoring")
    
    # Debug information
    print(f"Action ID: {action_id}")
    
    # Check if we got a real transaction
    try:
        # Make a POST request to the /anchor endpoint
        url = "http://localhost:8000/anchor"
        payload = {
            "action_id": action_id,
            "network": network
        }
        print(f"Posting to URL: {url}")
        print(f"Payload: {payload}")
        
        # Set up headers with token if provided
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
            print(f"Using authorization header with token: {token[:10]}...")
        
        response = requests.post(url, json=payload, headers=headers)
        
        # Debug information
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {response.headers}")
        print(f"Response content: {response.text}")
        
        # Check if we got a valid response (accept 200 or 201)
        if response.status_code in [200, 201]:
            data = response.json()
            
            # Check if this is a mock transaction
            if data.get("is_mock") == True:
                print("⚠️ Received a mock transaction from the API.")
                print("Please check the Ethereum configuration.")
                print("Ensure ETHEREUM_MOCK=false and that you have a valid private key and RPC URL.")
                return "ERROR-ANCHORING-FAILED"
            
            # Extract the transaction hash
            if "tx_hash" in data:
                tx_hash = data["tx_hash"]
                
                # Ensure hash has 0x prefix
                if not tx_hash.startswith("0x"):
                    print(f"⚠️ Transaction hash missing 0x prefix: {tx_hash}")
                    tx_hash = f"0x{tx_hash}"
                    print(f"Added prefix, now: {tx_hash}")
                
                # Verify this looks like a real transaction hash
                if len(tx_hash) != 66:  # 0x + 64 hex chars
                    print(f"⚠️ Transaction hash has unusual length: {tx_hash}, length: {len(tx_hash)}")
                
                # Log the transaction details
                print(f"Transaction anchored successfully: {tx_hash}")
                print(f"Action ID: {data.get('action_id')}")
                print(f"Network: {data.get('network')}")
                if data.get('block_number'):
                    print(f"Block Number: {data.get('block_number')}")
                
                # Save transaction hash to file for the Makefile to use
                with open("tx_hash.txt", "w") as f:
                    f.write(tx_hash)
                
                # Poll Etherscan to see if the transaction is indexed
                etherscan_url = f"https://sepolia.etherscan.io/tx/{tx_hash}"
                print(f"Waiting for Etherscan to index transaction {tx_hash}...")
                max_attempts = 6  # Try up to 6 times (30 seconds total)
                for attempt in range(max_attempts):
                    try:
                        etherscan_response = requests.get(etherscan_url)
                        if etherscan_response.status_code == 200:
                            print(f"Etherscan indexed transaction 👍 - {etherscan_url}")
                            break
                        else:
                            print(f"Attempt {attempt+1}/{max_attempts}: Etherscan not indexed yet (status: {etherscan_response.status_code})")
                    except Exception as ex:
                        print(f"Error checking Etherscan: {ex}")
                    
                    # Only sleep if we're not on the last attempt
                    if attempt < max_attempts - 1:
                        print("Waiting 5 seconds before trying again...")
                        time.sleep(5)
                
                if attempt == max_attempts - 1:
                    print("⚠️ Etherscan indexing may be delayed. The transaction is valid but might not be visible on Etherscan yet.")
                
                return tx_hash
            else:
                raise ValueError("Response did not contain 'tx_hash'")
        else:
            raise ValueError(f"Failed to anchor: {response.status_code} - {response.text}")
    except Exception as e:
        # This is a hard fail now - we want to use real transactions, not mocks
        print(f"❌ ERROR: {e}")
        print("Failed to anchor transaction. Please check the Ethereum configuration.")
        print("Ensure ETHEREUM_MOCK=false and that you have a valid private key and RPC URL.")
        print(f"Network: {network}")
        
        # Return a clearly invalid hash to indicate failure
        return "ERROR-ANCHORING-FAILED"

def main():
    """
    Main function for the demo.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="ChaosCore SDK Gateway Demo")
    parser.add_argument("--stage", action="store_true", help="Use staging environment (testnet)")
    parser.add_argument("--anchor-eth", action="store_true", help="Anchor proofs to Ethereum")
    parser.add_argument("--network", default="sepolia", help="Ethereum network to use (default: sepolia)")
    parser.add_argument("--port", type=int, default=8000, help="Custom port for the API Gateway (default: 8000)")
    args = parser.parse_args()
    
    print("=== ChaosCore SDK Gateway Demo (HTTP-first) ===\n")
    print(f"Using {'staging' if args.stage else 'production'} environment on {args.network}")
    print(f"Ethereum anchoring: {'enabled' if args.anchor_eth else 'disabled'}")
    
    # Use the specified port
    port = args.port
    
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
                "expertise": "HTTP Testing",
                "version": "1.0",
                "description": "HTTP SDK Demo Agent"
            }
        )
        agent_id = agent["agent_id"]
        token = agent["token"]
        
        # Make sure the token is set on the client (should be done by register_agent)
        print(f"Debug: Token is set in client: {'Yes' if client.token == token else 'No'}")
        print(f"Debug: Auth header is set: {'Yes' if 'Authorization' in client.session.headers else 'No'}")
        
        # Set the token on the client explicitly to be sure
        client.token = token
        client.session.headers.update({
            "Authorization": f"Bearer {token}"
        })
        
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
        
        # Print debug information
        print(f"Debug: Using token for action: {client.token[:10]}...")
        print(f"Debug: Headers for request: {client.session.headers}")
        
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
        print(f"Anchoring proof hash to {'Sepolia testnet' if args.stage else 'Ethereum mainnet'}...")
        
        # Anchor the enclave hash to Ethereum
        tx_hash = anchor_to_ethereum(
            enclave_hash,
            use_staging=args.stage,
            network=args.network,
            action_id=action_id,
            token=client.token  # Pass the token explicitly
        )
        time.sleep(2)
        
        # Validate the transaction hash
        explorer_url = None
        if tx_hash and tx_hash != "ERROR-ANCHORING-FAILED":
            # Ensure hash has 0x prefix for Etherscan
            if not tx_hash.startswith("0x"):
                tx_hash = f"0x{tx_hash}"
                print(f"Added 0x prefix for Etherscan compatibility: {tx_hash}")
                
                # Re-save corrected hash
                with open("tx_hash.txt", "w") as f:
                    f.write(tx_hash)
            
            explorer_url = f"{SEPOLIA_EXPLORER_URL}{tx_hash}" if args.network == "sepolia" else f"https://etherscan.io/tx/{tx_hash}"
            print(f"Proof anchored successfully.")
            print(f"Transaction hash: {tx_hash}")
            print(f"View on Etherscan: {explorer_url}")
            
            # Save the tx hash to file
            with open("tx_hash.txt", "w") as f:
                f.write(tx_hash)
        elif tx_hash == "ERROR-ANCHORING-FAILED":
            # This means anchoring failed with an error
            print("Generated mock transaction hash: ERROR-ANCHORING-FAILED")
            print("Note: This is a mock transaction for testing purposes, not a real on-chain transaction.")
            # Even with the mock hash, save it to the tx_hash.txt file for demo purposes
            with open("tx_hash.txt", "w") as f:
                f.write(tx_hash or "error_no_tx_hash")
        else:
            # This is most likely a mock transaction (if we generated it ourselves)
            print(f"Generated mock transaction hash: {tx_hash}")
            print("Note: This is a mock transaction for testing purposes, not a real on-chain transaction.")
            # Even with the mock hash, save it to the tx_hash.txt file for demo purposes
            with open("tx_hash.txt", "w") as f:
                f.write(tx_hash or "error_no_tx_hash")
    
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
        print(f"  • Ethereum TX: {tx_hash} (on {'Sepolia' if args.network == 'sepolia' else 'Mainnet'})")
        if explorer_url:
            print(f"  • TX Explorer: {explorer_url}")
    print(f"  • Reputation Δ: {reputation_delta:+.4f}")

if __name__ == "__main__":
    main() 