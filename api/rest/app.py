"""
FastAPI application server for ChaosChain Governance OS API.
"""

import sys
import os
import logging
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

# Add the parent directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from utils import get_logger
from api.models.database import engine, Base, get_db
from api.rest.routers import proposals, simulation, attestation, stream

# Create logger
logger = get_logger("api", verbose="-v" in sys.argv or "--verbose" in sys.argv)

# Initialize the database tables
logger.info("Initializing database tables...")
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="ChaosChain Governance OS API",
    description="API for ChaosChain Governance OS",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    logger.info("Health check requested")
    return {"status": "ok"}

# Include routers
logger.info("Setting up API routes...")
app.include_router(proposals.router)
app.include_router(simulation.router)
app.include_router(attestation.router)
app.include_router(stream.router)

# Mount the frontend static files
logger.info("Mounting frontend static files...")
app.mount("/ui", StaticFiles(directory="frontend/dist", html=True), name="ui")

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    logger.info("API starting up...")

@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    logger.info("API shutting down...") 