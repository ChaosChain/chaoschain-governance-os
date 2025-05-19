#!/usr/bin/env python3
"""
Test script for API Gateway fixes
"""

import sys
import logging
import json
import time
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Add the project root to Python path
import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# Import the ChaosCore SDK
from sdk.chaoscore.client import ChaosCore
from sdk.chaoscore.exceptions import ChaosCoreError

def main():
    """Test the complete API flow"""
    client = ChaosCore(base_url="http://localhost:8000")
    
    # Step 1: Check API health
    print("\n----- Step 1: Check API health -----")
    try:
        health = client.check_health()
        print(f"API Health: {health['status']}")
    except ChaosCoreError as e:
        print(f"Error checking API health: {e}")
        return
    
    # Step 2: Register a new agent
    print("\n----- Step 2: Register a new agent -----")
    try:
        agent = client.register_agent(
            name="Test Agent",
            email="test-agent@chaoscore.example",
            metadata={
                "role": "Test",
                "expertise": "Testing",
                "version": "1.0.0"
            }
        )
        agent_id = agent["agent_id"]
        token = agent["token"]
        print(f"Registered agent with ID: {agent_id}")
        print(f"Token: {token[:10]}...")
    except ChaosCoreError as e:
        print(f"Error registering agent: {e}")
        return
    
    # Step 3: Log an action
    print("\n----- Step 3: Log an action -----")
    try:
        action = client.log_action(
            action_type="TEST",
            description="Testing the API flow",
            data={
                "test_key": "test_value",
                "timestamp": datetime.now().isoformat()
            }
        )
        action_id = action["id"]
        print(f"Logged action with ID: {action_id}")
        print(f"Action details: {json.dumps(action, indent=2)}")
    except ChaosCoreError as e:
        print(f"Error logging action: {e}")
        return
    
    # Step 4: Record an outcome
    print("\n----- Step 4: Record an outcome -----")
    try:
        outcome = client.record_outcome(
            action_id=action_id,
            success=True,
            results={
                "result_key": "result_value",
                "timestamp": datetime.now().isoformat()
            },
            impact_score=0.75
        )
        print(f"Recorded outcome: {json.dumps(outcome, indent=2)}")
    except ChaosCoreError as e:
        print(f"Error recording outcome: {e}")
        return
    
    # Step 5: Create a studio
    print("\n----- Step 5: Create a studio -----")
    try:
        studio = client.create_studio(
            name="Test Studio",
            description="A test studio for API validation",
            metadata={
                "domain": "Testing",
                "version": "1.0.0"
            }
        )
        studio_id = studio["id"]
        print(f"Created studio with ID: {studio_id}")
        print(f"Studio details: {json.dumps(studio, indent=2)}")
    except ChaosCoreError as e:
        print(f"Error creating studio: {e}")
        return
    
    print("\n----- All tests completed successfully! -----")

if __name__ == "__main__":
    main() 