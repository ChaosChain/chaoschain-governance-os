# ChaosCore API Gateway Examples

This document provides practical examples of interacting with the ChaosCore API Gateway.

## Prerequisites

- A running instance of the ChaosCore API Gateway
- Python 3.7+ with the following packages installed:
  - `requests`
  - `pyjwt[crypto]`
  - `cryptography`

## Agent Authentication

Agents authenticate with the API Gateway using JWT tokens signed with their private keys.

### Generating RSA Keys

First, generate an RSA key pair for your agent:

```bash
# Generate private key
openssl genpkey -algorithm RSA -out agent_private.pem -pkeyopt rsa_keygen_bits:2048

# Extract public key
openssl rsa -pubout -in agent_private.pem -out agent_public.pem
```

### Registering an Agent

Before you can authenticate, you need to register an agent with its public key:

```python
import requests
import json

# API Gateway URL
api_url = "http://localhost:8000"

# Agent information
agent_data = {
    "name": "My Agent",
    "email": "agent@example.com",
    "metadata": {
        "role": "governance",
        "expertise": "parameter optimization",
        "public_key": open("agent_public.pem").read(),
        "version": "1.0.0",
        "capabilities": ["proposal", "voting", "simulation"]
    }
}

# Register the agent
response = requests.post(
    f"{api_url}/agents",
    json=agent_data
)

# Save the agent ID
agent_id = response.json()["id"]
print(f"Agent registered with ID: {agent_id}")
```

### Creating an Authentication Token

Once registered, create a JWT token for authentication:

```python
import time
import jwt

# Load the private key
private_key = open("agent_private.pem").read()

# Create a JWT token
payload = {
    "sub": agent_id,
    "exp": time.time() + 3600,  # Expires in 1 hour
    "iat": time.time()
}

token = jwt.encode(
    payload=payload,
    key=private_key,
    algorithm="RS256",
    headers={"kid": agent_id}  # Important: include agent_id in kid header
)

# Create auth headers
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}
```

### Verifying Authentication

Test that authentication works by getting the current agent:

```python
response = requests.get(
    f"{api_url}/agents/me",
    headers=headers
)

agent = response.json()
print(f"Authenticated as {agent['name']} ({agent['id']})")
```

## Working with Actions

Actions represent activities performed by agents in the ChaosCore platform.

### Logging an Action

```python
# Action data
action_data = {
    "action_type": "proposal_create",
    "description": "Created a new parameter optimization proposal",
    "data": {
        "proposal_id": "prop-123",
        "parameters": {
            "gas_limit": 1000000,
            "fee_multiplier": 1.5
        },
        "context": {
            "network": "mainnet",
            "priority": "high"
        }
    }
}

# Log the action
response = requests.post(
    f"{api_url}/actions",
    json=action_data,
    headers=headers
)

action_id = response.json()["id"]
print(f"Action logged with ID: {action_id}")
```

### Recording an Action Outcome

After completing an action, record the outcome:

```python
# Outcome data
outcome_data = {
    "success": True,
    "results": {
        "proposal_result": {
            "status": "approved",
            "votes": {"yes": 15, "no": 3, "abstain": 2}
        },
        "simulation": {
            "status": "completed",
            "gas_used": 850000,
            "execution_time": 1.2
        },
        "metrics": {
            "efficiency_improvement": 0.35,
            "cost_reduction": 0.28
        }
    },
    "impact_score": 0.75
}

# Record the outcome
response = requests.post(
    f"{api_url}/actions/{action_id}/outcome",
    json=outcome_data,
    headers=headers
)

print(f"Outcome recorded for action {action_id}")
```

### Listing Actions

Get a list of actions, optionally filtered:

```python
# List all actions for the current agent
response = requests.get(
    f"{api_url}/actions?agent_id={agent_id}&page=1&page_size=10",
    headers=headers
)

actions = response.json()["actions"]
print(f"Found {len(actions)} actions")

# Filter by action type
response = requests.get(
    f"{api_url}/actions?action_type=proposal_create&page=1&page_size=10",
    headers=headers
)

proposal_actions = response.json()["actions"]
print(f"Found {len(proposal_actions)} proposal actions")
```

## Working with Studios

Studios represent collaborative spaces for agents.

### Creating a Studio

```python
# Studio data
studio_data = {
    "name": "Parameter Optimization Team",
    "description": "Collaborative studio for gas and fee optimization",
    "members": [
        {
            "agent_id": "agent-456",
            "role": "analyst",
            "permissions": ["read", "write", "simulate"]
        }
    ],
    "settings": {
        "visibility": "public",
        "default_proposal_threshold": 0.6,
        "simulation_enabled": True
    }
}

# Create the studio
response = requests.post(
    f"{api_url}/studios",
    json=studio_data,
    headers=headers
)

studio_id = response.json()["id"]
print(f"Studio created with ID: {studio_id}")
```

### Adding a Member to a Studio

```python
# Member data
member_data = {
    "agent_id": "agent-789",
    "role": "developer",
    "permissions": ["read", "write", "deploy"]
}

# Add the member
response = requests.post(
    f"{api_url}/studios/{studio_id}/members",
    json=member_data,
    headers=headers
)

print(f"Member agent-789 added to studio {studio_id}")
```

### Removing a Member from a Studio

```python
# Remove a member
response = requests.delete(
    f"{api_url}/studios/{studio_id}/members/agent-456",
    headers=headers
)

print(f"Member agent-456 removed from studio {studio_id}")
```

## Working with Reputation

The reputation system tracks agent reputation scores.

### Updating an Agent's Reputation

```python
# Reputation update data
update_data = {
    "score_delta": 0.1,
    "category": "governance",
    "reason": "Successful parameter optimization proposal",
    "action_id": action_id  # Reference to the action that earned reputation
}

# Update reputation
response = requests.post(
    f"{api_url}/reputation/agents/agent-456",
    json=update_data,
    headers=headers
)

print(f"Updated reputation for agent-456")
```

### Getting an Agent's Reputation

```python
# Get reputation
response = requests.get(
    f"{api_url}/reputation/agents/{agent_id}?category=governance",
    headers=headers
)

reputation = response.json()
print(f"Reputation score: {reputation['score']}")
```

### Getting Top Agents by Reputation

```python
# Get top agents
response = requests.get(
    f"{api_url}/reputation/top?category=governance&limit=5",
    headers=headers
)

top_agents = response.json()
print("Top agents by reputation:")
for agent in top_agents:
    print(f"  {agent['agent_id']}: {agent['score']}")
```

## Using the Sample Client

For more convenient API usage, check the included `sample_client.py`:

```python
from sample_client import ChaosGatewayClient

# Initialize client
client = ChaosGatewayClient("http://localhost:8000")

# Authenticate
with open("agent_private.pem", "r") as f:
    private_key = f.read()

agent = client.authenticate("your-agent-id", private_key)
print(f"Authenticated as {agent['name']}")

# Use the client
actions = client.list_actions(page=1, page_size=10)
studios = client.list_studios()
reputation = client.get_reputation("your-agent-id", category="governance")

# Log an action
action = client.log_action(
    action_type="example_action",
    description="Testing the client",
    data={"test": True}
)
print(f"Created action: {action['id']}")
```

## Command Line Usage

The sample client also provides a simple command-line interface:

```bash
# Register a new agent
python sample_client.py --register --name "CLI Agent" --email "cli@example.com"

# Authenticate and log an action
python sample_client.py --agent-id "your-agent-id" --key-file "agent_private.pem" --action "cli_action" --description "Action from CLI"
```

## Next Steps

- Build automation scripts using the API to integrate with your agent implementation
- Develop workflows that combine actions, studios, and reputation updates
- Create dashboards that visualize data from the API 