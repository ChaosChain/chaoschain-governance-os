"""
ChaosCore API Gateway

This is the main entry point for the ChaosCore API Gateway.
"""
import os
from typing import Dict, Any
import logging
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

# Core imports
from chaoscore.core.database_adapter import PostgreSQLAdapter
from chaoscore.core.agent_registry import AgentRegistryInterface
from chaoscore.core.proof_of_agency import ProofOfAgencyInterface
from chaoscore.core.secure_execution import SecureExecutionEnvironment
from chaoscore.core.reputation import ReputationSystem
from chaoscore.core.studio import StudioManager

# Database imports
from chaoscore.core.database_adapter import (
    PostgreSQLAgentRegistry,
    PostgreSQLProofOfAgency,
    PostgreSQLReputationSystem
)
from chaoscore.core.secure_execution_sgx import SGXSecureExecutionEnvironment

# Auth
from api_gateway.auth.jwt_auth import JWTAuth

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

# Core components
db = None
agent_registry = None
proof_of_agency = None
secure_execution = None
reputation_system = None
studio_manager = None
jwt_auth = None


@app.on_event("startup")
async def startup_event():
    """Initialize components on startup."""
    global db, agent_registry, proof_of_agency, secure_execution, reputation_system, studio_manager, jwt_auth
    
    logger.info(f"Starting API Gateway in {ENV} environment")
    
    # Initialize database
    db = PostgreSQLAdapter()
    agent_registry = PostgreSQLAgentRegistry(db)
    proof_of_agency = PostgreSQLProofOfAgency(db)
    reputation_system = PostgreSQLReputationSystem(db)
    
    # Initialize secure execution
    if USE_SGX:
        logger.info(f"Using SGX Secure Execution Environment at {SGX_URL}")
        try:
            secure_execution = SGXSecureExecutionEnvironment(SGX_URL)
            enclave_info = secure_execution.get_enclave_info()
            logger.info(f"Connected to SGX enclave with hash: {enclave_info.get('enclave_hash', 'unknown')}")
        except Exception as e:
            logger.warning(f"Could not connect to SGX enclave: {e}")
            logger.warning("Falling back to in-memory secure execution")
            from chaoscore.core.secure_execution import InMemorySecureExecution
            secure_execution = InMemorySecureExecution()
    else:
        logger.info("Using in-memory secure execution (SGX mocked)")
        from chaoscore.core.secure_execution import InMemorySecureExecution
        secure_execution = InMemorySecureExecution()
    
    # Initialize studio manager
    from chaoscore.core.studio import InMemoryStudioManager
    studio_manager = InMemoryStudioManager()
    
    # Initialize Ethereum client if needed
    if USE_ETHEREUM:
        logger.info(f"Using Ethereum anchoring with provider: {ETHEREUM_PROVIDER_URL}")
        logger.info(f"Contract address: {ETHEREUM_CONTRACT_ADDRESS}")
        
        from chaoscore.core.ethereum import EthereumClient
        ethereum_client = EthereumClient(
            contract_address=ETHEREUM_CONTRACT_ADDRESS,
            provider_url=ETHEREUM_PROVIDER_URL
        )
        
        # Connect with the proof of agency
        proof_of_agency.set_anchor_client(ethereum_client)
    
    # Initialize JWT auth
    jwt_auth = JWTAuth(agent_registry)
    
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
    # Create dependency functions
    def get_agent_registry() -> AgentRegistryInterface:
        return agent_registry
    
    def get_proof_of_agency() -> ProofOfAgencyInterface:
        return proof_of_agency
    
    def get_secure_execution() -> SecureExecutionEnvironment:
        return secure_execution
    
    def get_reputation_system() -> ReputationSystem:
        return reputation_system
    
    def get_studio_manager() -> StudioManager:
        return studio_manager
    
    def get_jwt_auth() -> JWTAuth:
        return jwt_auth
    
    # Initialize routers with dependencies
    app.include_router(
        agents.router,
        prefix="/agents",
        tags=["Agents"],
        dependencies=[Depends(get_agent_registry), Depends(get_jwt_auth)]
    )
    
    app.include_router(
        actions.router,
        prefix="/actions",
        tags=["Actions"],
        dependencies=[Depends(get_proof_of_agency), Depends(get_jwt_auth)]
    )
    
    app.include_router(
        studios.router,
        prefix="/studios",
        tags=["Studios"],
        dependencies=[Depends(get_studio_manager), Depends(get_jwt_auth)]
    )
    
    app.include_router(
        reputation.router,
        prefix="/reputation",
        tags=["Reputation"],
        dependencies=[Depends(get_reputation_system), Depends(get_jwt_auth)]
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
    if not db or not agent_registry or not proof_of_agency or not secure_execution:
        raise HTTPException(status_code=500, detail="API Gateway not fully initialized")
    
    return {
        "status": "healthy",
        "environment": ENV,
        "components": {
            "database": "connected" if db.conn and not db.conn.closed else "disconnected",
            "agent_registry": "available",
            "proof_of_agency": "available" + (" (with anchoring)" if USE_ETHEREUM else ""),
            "secure_execution": "available" + (" (SGX)" if USE_SGX else " (in-memory)"),
            "reputation_system": "available",
            "studio_manager": "available",
        }
    } 