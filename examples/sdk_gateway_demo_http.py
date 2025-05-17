#!/usr/bin/env python3
"""
SDK Gateway Demo (HTTP-first)

This demo demonstrates how to use the ChaosCore HTTP-first SDK to interact with the API Gateway.
"""

import json
import logging
import time
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

def main():
    """
    Main function for the demo.
    """
    print("=== ChaosCore SDK Gateway Demo (HTTP-first) ===\n")
    
    # Create a client
    print("Connecting to ChaosCore API Gateway...")
    client = ChaosCore(base_url="http://localhost:8000")
    
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
        agent = client.register_agent(
            name="Demo Agent HTTP",
            email="demo-http@chaoscore.example",
            metadata={
                "role": "Demo",
                "framework": "HTTP SDK",
                "capabilities": ["API", "HTTP", "Testing"]
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
        action = client.log_action(
            action_type="ANALYZE",
            description="Analyzing performance metrics",
            data={
                "metrics": ["cpu", "memory", "network"],
                "timeframe": "last_24h",
                "importance": "high"
            }
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
        outcome = client.record_outcome(
            action_id=action_id,
            success=True,
            results={
                "findings": "CPU usage spike at 14:00",
                "root_cause": "Batch job scheduling conflict",
                "recommendations": [
                    "Stagger batch job scheduling",
                    "Increase CPU allocation"
                ]
            },
            impact_score=0.75
        )
        print(f"Recorded outcome: {outcome['id']}")
    except ChaosCoreError as e:
        print(f"Error recording outcome: {e}")
    
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
                "metrics": ["throughput", "latency", "error_rate"]
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
    
    # Query reputation
    print("\n=== Querying Reputation ===")
    try:
        print(f"Querying reputation for agent {agent_id}...")
        reputation = client.get_agent_reputation(agent_id)
        print(f"Agent reputation score: {reputation['score']:.4f}")
        print(f"Trust level: {reputation['trust_level']}")
    except ChaosCoreError as e:
        print(f"Error querying reputation: {e}")
    
    print("\n=== JWT Auth Status ===")
    try:
        auth_status = client.get_auth_status()
        print("Authentication System Status:")
        pprint(auth_status)
    except ChaosCoreError as e:
        print(f"Error getting auth status: {e}")
    
    # Wait for a second to let things process
    time.sleep(1)
    
    print("\n=== Simulating SGX Enclave Processing ===")
    print("Executing secure computation in SGX enclave...")
    time.sleep(2)  # Simulate enclave computation
    print("Enclave computation complete.\n")
    
    print("\n=== Simulating Ethereum Anchoring ===")
    print("Generating proof for outcome...")
    time.sleep(1)
    print("Anchoring proof hash to Ethereum...")
    time.sleep(2)
    print("Proof anchored successfully. Transaction hash: 0x1a2b3c4d5e6f...")
    
    print("\n=== Demo Complete ===")
    print("The ChaosCore HTTP-first SDK demo has completed successfully.")

if __name__ == "__main__":
    main() 