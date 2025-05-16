# ChaosCore API Gateway

The ChaosCore API Gateway serves as the main entry point for interacting with the ChaosCore platform. It provides a REST API for managing agents, actions, studios, and reputation within the platform.

## Overview

The API Gateway is built using FastAPI and provides the following features:

- JWT-based authentication using agent private keys
- Agent management (create, list, get)
- Action logging and outcome recording
- Studio management (create, list, get, add/remove members)
- Reputation tracking and updates
- Integration with PostgreSQL for persistence
- Optional SGX secure execution
- Optional Ethereum anchoring for proof of agency

## Architecture

The API Gateway follows a modular architecture with the following components:

- **Main Application**: The central FastAPI application that coordinates all components
- **Authentication**: JWT-based authentication using agent private keys
- **Routers**: Modular endpoints for different resource types
- **Core Services**: Integration with ChaosCore components (agent registry, proof of agency, etc.)

## Authentication

Authentication is performed using JWT tokens signed by the agent's private key. The token is verified using the agent's public key, which is retrieved from the AgentRegistry.

To authenticate:

1. Create a JWT token signed by your agent's private key
2. Include the agent ID in the token's `kid` header
3. Send the token in the Authorization header with the Bearer scheme

Example token creation:
```python
import jwt
import time

# Create token payload
payload = {
    "sub": "your-agent-id",
    "exp": time.time() + 3600,  # 1 hour
    "iat": time.time()
}

# Sign token with private key
token = jwt.encode(
    payload=payload,
    key=private_key_pem,
    algorithm="RS256",
    headers={"kid": "your-agent-id"}
)

# Use in HTTP request
headers = {"Authorization": f"Bearer {token}"}
```

## API Endpoints

### Agents

- `POST /agents`: Create a new agent
- `GET /agents`: List agents
- `GET /agents/{agent_id}`: Get an agent by ID
- `GET /agents/me`: Get the current authenticated agent

### Actions

- `POST /actions`: Log an action
- `POST /actions/{action_id}/outcome`: Record an action outcome
- `GET /actions`: List actions
- `GET /actions/{action_id}`: Get an action by ID

### Studios

- `POST /studios`: Create a new studio
- `GET /studios`: List studios
- `GET /studios/{studio_id}`: Get a studio by ID
- `POST /studios/{studio_id}/members`: Add a member to a studio
- `DELETE /studios/{studio_id}/members/{agent_id}`: Remove a member from a studio

### Reputation

- `GET /reputation/agents/{agent_id}`: Get an agent's reputation score
- `GET /reputation/agents/{agent_id}/history`: Get an agent's reputation history
- `POST /reputation/agents/{agent_id}`: Update an agent's reputation
- `GET /reputation/top`: Get top agents by reputation

## Configuration

The API Gateway can be configured using environment variables:

- `CHAOSCORE_ENV`: Environment (development, test, staging, production)
- `SGX_MOCK`: Whether to mock SGX secure execution (true/false)
- `SGX_ENCLAVE_URL`: URL of the SGX enclave
- `ETHEREUM_MOCK`: Whether to mock Ethereum anchoring (true/false)
- `ETHEREUM_PROVIDER_URL`: URL of the Ethereum provider
- `ETHEREUM_CONTRACT_ADDRESS`: Address of the Ethereum contract
- `JWT_SECRET`: Secret key for JWT (not used with RS256)
- `DATABASE_URL`: PostgreSQL connection string

## Running in Development

To run the API Gateway in development mode:

```bash
# Set environment variables
export CHAOSCORE_ENV=development
export SGX_MOCK=true
export ETHEREUM_MOCK=true
export DATABASE_URL=postgresql://user:password@localhost:5432/chaoscore

# Start the API
uvicorn api_gateway.main:app --reload
```

## Running in Production

For production deployments, it's recommended to:

1. Use a proper ASGI server like Uvicorn or Gunicorn
2. Enable SGX secure execution
3. Enable Ethereum anchoring
4. Configure proper CORS headers
5. Use a reverse proxy like Nginx

Example production startup:

```bash
# Set environment variables
export CHAOSCORE_ENV=production
export SGX_MOCK=false
export SGX_ENCLAVE_URL=http://sgx-enclave:7000
export ETHEREUM_MOCK=false
export ETHEREUM_PROVIDER_URL=https://mainnet.infura.io/v3/your-api-key
export ETHEREUM_CONTRACT_ADDRESS=0x1234567890123456789012345678901234567890
export DATABASE_URL=postgresql://user:password@postgres:5432/chaoscore

# Start with Gunicorn (multiple workers)
gunicorn api_gateway.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## API Documentation

Once the API Gateway is running, you can access the auto-generated Swagger documentation at `/docs` and the ReDoc documentation at `/redoc`.

## Example Usage

Here's an example of using the API Gateway with Python:

```python
import requests
import jwt
import time

# API base URL
base_url = "http://localhost:8000"

# Agent private key (from secure storage)
private_key = """
-----BEGIN RSA PRIVATE KEY-----
...
-----END RSA PRIVATE KEY-----
"""

# Create a JWT token
agent_id = "your-agent-id"
payload = {
    "sub": agent_id,
    "exp": time.time() + 3600,
    "iat": time.time()
}

token = jwt.encode(
    payload=payload,
    key=private_key,
    algorithm="RS256",
    headers={"kid": agent_id}
)

# Auth header
headers = {
    "Authorization": f"Bearer {token}"
}

# Log an action
action_data = {
    "action_type": "proposal_create",
    "description": "Created a new governance proposal",
    "data": {
        "proposal_id": "prop-123",
        "parameters": {"param1": "value1"},
        "context": {"context1": "value1"}
    }
}

response = requests.post(
    f"{base_url}/actions",
    json=action_data,
    headers=headers
)

print(f"Action created: {response.json()}")
```

## Monitoring and Health Check

The API Gateway provides a health check endpoint at `/health` that returns the status of all components.

## Security Considerations

- Always use HTTPS in production
- Keep agent private keys secure
- Limit access to administrative endpoints
- Configure proper CORS headers
- Consider using rate limiting for production deployments 