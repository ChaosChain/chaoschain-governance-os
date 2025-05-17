"""
ChaosCore API Gateway

This module provides the main FastAPI application for the ChaosCore API Gateway.
"""

import logging
import uuid
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import PlainTextResponse

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import metrics
from api_gateway.metrics import (
    start_timer, end_timer, get_metrics,
    ACTIVE_AGENTS, AGENT_REGISTRATIONS, ACTIONS_LOGGED,
    OUTCOMES_RECORDED, STUDIOS_CREATED, TASKS_CREATED,
    REPUTATION_QUERIES
)

# Create the FastAPI app
app = FastAPI(
    title="ChaosCore API Gateway",
    description="API Gateway for the ChaosCore platform",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Import routers
from api_gateway.routers import agents, actions, studios, reputation
from api_gateway.auth.jwt_auth import router as auth_router

# Middleware to track request metrics
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    # Generate a request ID
    request_id = str(uuid.uuid4())
    
    # Get endpoint path for metrics
    endpoint = request.url.path
    method = request.method
    
    # Estimate request size
    request_size = 0
    if request.headers.get("content-length"):
        request_size = int(request.headers.get("content-length", "0"))
    
    # Start timing the request
    start_timer(request_id, endpoint, method)
    
    # Process the request
    try:
        response = await call_next(request)
        
        # Estimate response size
        response_size = 0
        if hasattr(response, "headers") and response.headers.get("content-length"):
            response_size = int(response.headers.get("content-length", "0"))
        
        # End timing the request
        end_timer(request_id, response.status_code, request_size, response_size)
        
        return response
    except Exception as e:
        # End timing with error status
        end_timer(request_id, 500, request_size, 0)
        raise e

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint, returns basic API information.
    """
    return {
        "name": "ChaosCore API Gateway",
        "version": "0.1.0",
        "status": "operational"
    }

# Health check endpoint
@app.get("/health", tags=["Monitoring"])
async def health_check():
    """
    Health check endpoint, returns the status of the API.
    """
    return {
        "status": "healthy"
    }

# Prometheus metrics endpoint
@app.get("/metrics", tags=["Monitoring"], response_class=PlainTextResponse)
async def metrics():
    """
    Prometheus metrics endpoint, returns metrics in Prometheus format.
    """
    return get_metrics()

# Custom OpenAPI schema
def custom_openapi():
    """
    Generate a custom OpenAPI schema for the API.
    """
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="ChaosCore API Gateway",
        version="0.1.0",
        description="API Gateway for the ChaosCore platform",
        routes=app.routes,
    )
    
    # Add custom components
    openapi_schema["components"] = {
        "securitySchemes": {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT"
            }
        }
    }
    
    # Add security requirement to all routes
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            if path not in ["/", "/health", "/metrics"]:  # Exclude public endpoints
                openapi_schema["paths"][path][method]["security"] = [{"BearerAuth": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

# Set custom OpenAPI schema
app.openapi = custom_openapi

# Register routers
app.include_router(agents.router, prefix="/agents", tags=["Agents"])
app.include_router(actions.router, prefix="/actions", tags=["Actions"])
app.include_router(studios.router, prefix="/studios", tags=["Studios"])
app.include_router(reputation.router, prefix="/reputation", tags=["Reputation"])
app.include_router(auth_router)

# Main entry point for running the application directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api_gateway.main:app", host="0.0.0.0", port=8000, reload=True) 