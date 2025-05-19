#!/usr/bin/env python3
"""
Authentication Debug Script

This script tests authentication with the ChaosCore API Gateway.
"""

import json
import logging
import sys
import os
import requests

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Import the ChaosCore SDK
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from sdk.chaoscore.client import ChaosCore
from sdk.chaoscore.exceptions import ChaosCoreError

def main():
    # Create a client
    print("Creating ChaosCore client...")
    client = ChaosCore(base_url="http://localhost:8000")
    
    # Check API health
    try:
        health = client.check_health()
        print(f"API Health: {health['status']}")
    except ChaosCoreError as e:
        print(f"Error checking API health: {e}")
        return
    
    # Register a new agent
    try:
        print("Registering a new agent...")
        agent = client.register_agent(
            name="Auth Debug Agent",
            email="auth-debug@chaoscore.example",
            metadata={
                "role": "Debug",
                "purpose": "Authentication Testing"
            }
        )
        agent_id = agent["agent_id"]
        token = agent["token"]
        print(f"Registered agent with ID: {agent_id}")
        print(f"Token: {token}")
        
        # Print current headers
        print(f"Client headers after registration:")
        print(json.dumps(dict(client.session.headers), indent=2))
    except ChaosCoreError as e:
        print(f"Error registering agent: {e}")
        return
    
    # Try a direct request with the token
    print("\nTesting direct request with token...")
    try:
        direct_headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        action_data = {
            "action_type": "DEBUG",
            "description": "Testing authentication",
            "data": {
                "test": "value"
            }
        }
        
        response = requests.post(
            "http://localhost:8000/actions",
            headers=direct_headers,
            json=action_data
        )
        
        print(f"Direct request status: {response.status_code}")
        if response.status_code == 201:
            action_id = response.json()["id"]
            print(f"Action logged with ID: {action_id}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error with direct request: {e}")
    
    # Try with the client
    print("\nTesting client request...")
    try:
        action = client.log_action(
            action_type="DEBUG",
            description="Testing client authentication",
            data={
                "test": "value",
                "method": "client"
            }
        )
        action_id = action["id"]
        print(f"Action logged with ID: {action_id}")
    except ChaosCoreError as e:
        print(f"Error logging action with client: {e}")
    
    # Check if the token is being included in the client requests
    print("\nDebug client request...")
    try:
        # Monkey patch the _request method to show headers
        original_request = client._request
        
        def debug_request(method, endpoint, params=None, data=None, headers=None):
            print(f"Request headers: {json.dumps(dict(client.session.headers), indent=2)}")
            return original_request(method, endpoint, params, data, headers)
        
        client._request = debug_request
        
        # Try another request
        client.log_action(
            action_type="DEBUG",
            description="Testing headers",
            data={
                "test": "headers",
                "time": "now"
            }
        )
    except ChaosCoreError as e:
        print(f"Error in debug request: {e}")

if __name__ == "__main__":
    main() 