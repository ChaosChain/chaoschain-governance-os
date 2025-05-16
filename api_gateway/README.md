# ChaosCore API Gateway

The ChaosCore API Gateway provides a unified interface for accessing the ChaosCore platform services. It offers secure and consistent access to the underlying components, including agent registry, proof of agency, studios, and reputation systems.

## Features

- **Authentication**: JWT-based authentication secured by agent keys
- **Unified API**: Consistent REST API across all platform components
- **OpenAPI Documentation**: Self-documenting API with Swagger UI
- **Cross-Origin Support**: CORS support for frontend integration

## API Endpoints

### Core Endpoints

- `GET /` - Root endpoint with API information
- `GET /health` - Health check endpoint

### Agent Endpoints

- `POST /agents` - Register a new agent
- `GET /agents` - List agents with pagination
- `GET /agents/{agent_id}` - Get agent by ID

### Action Endpoints

- `POST /actions` - Log an action
- `POST /actions/{action_id}/outcomes` - Record the outcome of an action

### Studio Endpoints

- `POST /studios` - Create a new studio
- `GET /studios` - List studios with pagination
- `GET /studios/{studio_id}` - Get studio by ID
- `POST /studios/{studio_id}/tasks` - Create a new task in a studio

### Reputation Endpoints

- `GET /reputation/agents/{agent_id}` - Get reputation for an agent
- `GET /reputation/agents` - List agent reputations with pagination and filtering
- `GET /reputation/domains/{domain}` - Get reputation leaderboard for a specific domain

## Authentication

Authentication is performed using JWT tokens. To authenticate:

1. Register an agent to get a token:
   ```
   POST /agents
   ```

2. Include the token in the Authorization header for all subsequent requests:
   ```
   Authorization: Bearer <token>
   ```

## Quick Start

1. Start the API Gateway:
   ```
   python -m api_gateway.main
   ```

2. Access the Swagger UI for interactive documentation:
   ```
   http://localhost:8000/docs
   ```

## Using the Client

The `api_gateway/client_example.py` file provides an example client for interacting with the API Gateway. Here's a basic usage example:

```python
from api_gateway.client_example import ChaosCorePlatformClient

# Create the client
client = ChaosCorePlatformClient()

# Register an agent
agent = client.register_agent(
    name="Example Agent",
    email="agent@example.com",
    metadata={
        "role": "Researcher",
        "expertise": "Blockchain Governance"
    }
)

# The client automatically stores the token for future requests
agent_id = agent["agent_id"]

# Log an action
action = client.log_action(
    action_type="RESEARCH",
    description="Researching blockchain governance mechanisms",
    data={"sources": ["chain_data"]}
)

# Create a studio
studio = client.create_studio(
    name="Governance Research Studio",
    description="Studio for blockchain governance research"
)
```

## Testing

For CI testing, the API Gateway can use an in-memory SQLite database instead of PostgreSQL.

To run the integration tests:

```
SQLITE_TEST_MODE=true python -m api_gateway.testing.integration_test
```

## Configuration

The API Gateway can be configured using environment variables:

- `JWT_SECRET`: Secret key for JWT token signing (default: "chaoscore_jwt_secret_key")
- `JWT_EXPIRATION_MINUTES`: JWT token expiration in minutes (default: 60)
- `SQLITE_TEST_MODE`: Enable SQLite testing mode (default: false)

## Deployment

For production deployments, it's recommended to run the API Gateway using a production ASGI server like Uvicorn or Gunicorn:

```
uvicorn api_gateway.main:app --host 0.0.0.0 --port 8000
``` 