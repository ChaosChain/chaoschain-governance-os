#!/usr/bin/env python3
"""
Direct test of outcomes endpoint
"""

import requests
import json
import sys

# Capture token from command line
if len(sys.argv) != 3:
    print("Usage: python test_outcome.py <action_id> <token>")
    sys.exit(1)

action_id = sys.argv[1]
token = sys.argv[2]

# Endpoint
url = f"http://localhost:8000/actions/{action_id}/outcomes"

# Headers
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Data
data = {
    "success": True,
    "impact_score": 0.5,
    "results": {
        "test": "value"
    }
}

# Make the request
print(f"Sending POST to {url}")
print(f"Headers: {json.dumps(headers)}")
print(f"Data: {json.dumps(data)}")

try:
    response = requests.post(url, headers=headers, json=data)
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.text}")
    response.raise_for_status()
except Exception as e:
    print(f"Error: {e}") 