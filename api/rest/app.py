"""
Main FastAPI application.
"""

import sys
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from api.rest.routers import proposals, simulation, attestation
from api.auth.api_key import get_api_key
from api.models import Base, engine
from utils import get_logger

# Configure logging
verbose = "--verbose" in sys.argv
logger = get_logger("api", verbose=verbose)

# Create database tables
logger.info("Initializing database tables")
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="ChaosChain Governance OS API",
    description="API for the ChaosChain Governance OS",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
logger.info("Setting up API routes")
app.include_router(proposals.router)
app.include_router(simulation.router)
app.include_router(attestation.router)


@app.get("/", tags=["health"])
async def root():
    """
    Health check endpoint.
    
    Returns:
        Health status
    """
    logger.debug("Health check requested")
    return {"status": "ok", "message": "ChaosChain Governance OS API is running"}


@app.on_event("startup")
async def startup_event():
    """
    Run when the application starts.
    """
    logger.info("🚀 ChaosChain Governance OS API started")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Run when the application shuts down.
    """
    logger.info("👋 ChaosChain Governance OS API shutting down") 