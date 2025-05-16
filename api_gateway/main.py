"""
ChaosCore API Gateway

This is the main entry point for the ChaosCore API Gateway.
"""
import os
from typing import Dict, Any, Callable
import logging
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

# Core imports
from chaoscore.core.database_adapter import (
    get_database_adapter,
    PostgreSQLAgentRegistry,
    PostgreSQLProofOfAgency,
    PostgreSQLReputationSystem
)
from chaoscore.core.agent_registry import AgentRegistryInterface
from chaoscore.core.proof_of_agency import ProofOfAgencyInterface
from chaoscore.core.secure_execution import SecureExecutionEnvironment, InMemorySecureExecution
from chaoscore.core.secure_execution_sgx import SGXSecureExecutionEnvironment
from chaoscore.core.reputation import ReputationSystem
from chaoscore.core.studio import StudioManager, InMemoryStudioManager
from chaoscore.core.ethereum import EthereumClient

# Auth
from api_gateway.auth.jwt_auth import JWTAuth

# Dependencies
import api_gateway.dependencies as deps

# Router imports
from api_gateway.routers import agents, actions, studios, reputation

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("api_gateway")

# Environment variables
ENV = os.environ.get("CHAOSCORE_ENV", "development")
USE_SGX = os.environ.get("SGX_MOCK", "false").lower() != "true"
SGX_URL = os.environ.get("SGX_ENCLAVE_URL", "http://localhost:7000")
USE_ETHEREUM = os.environ.get("ETHEREUM_MOCK", "false").lower() != "true" and ENV in ("staging", "production")
ETHEREUM_PROVIDER_URL = os.environ.get("ETHEREUM_PROVIDER_URL", "https://goerli.infura.io/v3/your-api-key")
ETHEREUM_CONTRACT_ADDRESS = os.environ.get("ETHEREUM_CONTRACT_ADDRESS", "0x1234567890123456789012345678901234567890")

# Create app
app = FastAPI(
    title="ChaosCore API Gateway",
    description="API Gateway for the ChaosCore platform",
    version="1.0.0",
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Core components (initialized during startup)
db = None


@app.on_event("startup")
async def startup_event():
    """Initialize components on startup."""
    global db
    
    logger.info(f"Starting API Gateway in {ENV} environment")
    
    # Initialize database adapter
    try:
        db = get_database_adapter()
        db.create_tables()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
    
    # Initialize core components
    deps.agent_registry = PostgreSQLAgentRegistry(db)
    deps.proof_of_agency = PostgreSQLProofOfAgency(db)
    deps.reputation_system = PostgreSQLReputationSystem(db)
    
    # Initialize secure execution
    if USE_SGX:
        logger.info(f"Using SGX Secure Execution Environment at {SGX_URL}")
        try:
            deps.secure_execution = SGXSecureExecutionEnvironment(SGX_URL)
            enclave_info = deps.secure_execution.get_enclave_info()
            logger.info(f"Connected to SGX enclave with hash: {enclave_info.get('enclave_hash', 'unknown')}")
        except Exception as e:
            logger.warning(f"Could not connect to SGX enclave: {e}")
            logger.warning("Falling back to in-memory secure execution")
            deps.secure_execution = InMemorySecureExecution()
    else:
        logger.info("Using in-memory secure execution (SGX mocked)")
        deps.secure_execution = InMemorySecureExecution()
    
    # Initialize studio manager
    deps.studio_manager = InMemoryStudioManager()
    
    # Initialize Ethereum client if needed
    if USE_ETHEREUM:
        logger.info(f"Using Ethereum anchoring with provider: {ETHEREUM_PROVIDER_URL}")
        logger.info(f"Contract address: {ETHEREUM_CONTRACT_ADDRESS}")
        
        ethereum_client = EthereumClient(
            contract_address=ETHEREUM_CONTRACT_ADDRESS,
            provider_url=ETHEREUM_PROVIDER_URL
        )
        
        # Connect with the proof of agency
        deps.proof_of_agency.set_anchor_client(ethereum_client)
    
    # Initialize JWT auth
    deps.jwt_auth = JWTAuth(deps.agent_registry)
    
    # Configure routers with dependencies
    configure_routers()
    
    logger.info("API Gateway startup completed")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    logger.info("Shutting down API Gateway")
    if db:
        db.close()


def configure_routers():
    """Configure routers with dependencies."""
    # Configure the routers with dependencies
    app.include_router(
        agents.router,
        prefix="/agents",
        tags=["Agents"],
        dependencies=[Depends(deps.get_agent_registry), Depends(deps.get_jwt_auth)]
    )
    
    app.include_router(
        actions.router,
        prefix="/actions",
        tags=["Actions"],
        dependencies=[Depends(deps.get_proof_of_agency), Depends(deps.get_jwt_auth)]
    )
    
    app.include_router(
        studios.router,
        prefix="/studios",
        tags=["Studios"],
        dependencies=[Depends(deps.get_studio_manager), Depends(deps.get_jwt_auth)]
    )
    
    app.include_router(
        reputation.router,
        prefix="/reputation",
        tags=["Reputation"],
        dependencies=[Depends(deps.get_reputation_system), Depends(deps.get_jwt_auth)]
    )


# Custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Add security scheme for JWT
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT token signed by agent's private key. The agent_id must be included in the token's 'kid' header."
        }
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "ChaosCore API Gateway",
        "version": "1.0.0",
        "environment": ENV,
        "status": "running",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    if not db or not deps.agent_registry or not deps.proof_of_agency or not deps.secure_execution:
        raise HTTPException(status_code=500, detail="API Gateway not fully initialized")
    
    db_status = "connected"
    try:
        # Test database connection
        db.execute("SELECT 1")
        db.fetchone()
    except Exception as e:
        db_status = f"disconnected ({str(e)})"
    
    return {
        "status": "healthy",
        "environment": ENV,
        "components": {
            "database": db_status,
            "agent_registry": "available",
            "proof_of_agency": "available" + (" (with anchoring)" if USE_ETHEREUM else ""),
            "secure_execution": "available" + (" (SGX)" if USE_SGX else " (in-memory)"),
            "reputation_system": "available",
            "studio_manager": "available",
        }
    } 