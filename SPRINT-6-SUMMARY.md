# Sprint 6 – Hardening & Load Testing

This sprint focused on hardening the API Gateway implementation and adding load testing capabilities to ensure the system can handle the required load with acceptable performance.

## Key Deliverables

### 1. Load Testing with k6

- Created a comprehensive k6 load test script (`tests/load/api_gateway_load.js`) that:
  - Tests all main API endpoints (agents, actions, studios, tasks, reputation)
  - Simulates realistic user patterns with varied operations
  - Ramps up to 1,000 concurrent users
  - Targets 100 requests per second
  - Runs for 5 minutes
  - Validates p99 latency < 500ms

The script includes detailed metrics tracking and proper test assertions to ensure performance targets are met.

### 2. JWT Replay Protection & Key Rotation

- Added JWT ID (jti) claim for replay protection
- Implemented used token tracking to prevent token reuse
- Added a JWT key rotation endpoint (`/auth/rotate-key`)
- Implemented key rotation logic with previous/current/next key states
- Added authentication system status endpoint (`/auth/status`)

These enhancements greatly improve the security of the authentication system.

### 3. Enhanced Prometheus Metrics & Grafana Dashboard

- Added detailed histogram metrics for better insights:
  - Request latency percentiles (p50, p90, p95, p99)
  - Request sizes
  - Response sizes
  - Error rates by endpoint
- Added system metrics (CPU, memory)
- Added authentication metrics (validations, key rotations)
- Created a comprehensive Grafana dashboard (`deployments/grafana/dashboard.json`)

The dashboard provides real-time visibility into API performance, system health, and security metrics.

### 4. Multi-architecture Docker Build

- Created a multi-stage Dockerfile with optimizations for both build and runtime
- Configured for multi-architecture builds (AMD64 and ARM64)
- Added proper security measures (non-root user, minimized image size)
- Implemented health checks
- Added proper container labels
- Created GitHub Actions workflow for automated builds and publishing

The Docker setup ensures consistent deployments across different environments and architectures.

### 5. HTTP-first SDK

- Developed a modern HTTP-first SDK under `sdk/chaoscore/`
- Implemented a comprehensive client with methods for all API endpoints
- Added proper error handling and exceptions
- Provided clean documentation and type hints
- Created an example script demonstrating SDK usage (`examples/sdk_gateway_demo_http.py`)

The SDK provides a simple and intuitive way for applications to interact with the ChaosCore API Gateway.

## Running the Load Tests

To run the load tests:

1. Start the API Gateway server:
   ```bash
   export PYTHONPATH=$PYTHONPATH:$(pwd)
   uvicorn api_gateway.main:app --host 0.0.0.0 --port 8000
   ```

2. Run the k6 load test:
   ```bash
   k6 run tests/load/api_gateway_load.js
   ```

## Using the SDK

1. Install the SDK:
   ```bash
   cd sdk
   pip install -e .
   ```

2. Run the example:
   ```bash
   export PYTHONPATH=$PYTHONPATH:$(pwd)
   python examples/sdk_gateway_demo_http.py
   ```

## Building the Docker Image

Build for multiple architectures:
```bash
docker buildx build --platform linux/amd64,linux/arm64 -t chaoscore-api-gateway:latest .
```

Or use the GitHub Actions workflow by pushing to the main or hardening branch.

## Next Steps

1. Conduct additional load testing in production-like environments
2. Implement rate limiting for enhanced security and stability
3. Add distributed tracing for better performance insights
4. Expand the SDK with additional language bindings 