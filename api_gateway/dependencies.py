"""
Dependencies for the API Gateway.

This module defines dependencies for the FastAPI application.
"""
from typing import Dict, Any

from fastapi import Depends

from chaoscore.core.agent_registry import AgentRegistryInterface
from chaoscore.core.proof_of_agency import ProofOfAgencyInterface 
from chaoscore.core.reputation import ReputationSystem
from chaoscore.core.studio import StudioManager
from chaoscore.core.secure_execution import SecureExecutionEnvironment
from api_gateway.auth.jwt_auth import JWTAuth

# Global instances
# These will be initialized in the main app
agent_registry = None
proof_of_agency = None
secure_execution = None
reputation_system = None
studio_manager = None
jwt_auth = None


def get_agent_registry() -> AgentRegistryInterface:
    """
    Dependency for agent registry.
    
    Returns:
        Agent registry
    """
    return agent_registry


def get_proof_of_agency() -> ProofOfAgencyInterface:
    """
    Dependency for proof of agency.
    
    Returns:
        Proof of agency
    """
    return proof_of_agency


def get_secure_execution() -> SecureExecutionEnvironment:
    """
    Dependency for secure execution environment.
    
    Returns:
        Secure execution environment
    """
    return secure_execution


def get_reputation_system() -> ReputationSystem:
    """
    Dependency for reputation system.
    
    Returns:
        Reputation system
    """
    return reputation_system


def get_studio_manager() -> StudioManager:
    """
    Dependency for studio manager.
    
    Returns:
        Studio manager
    """
    return studio_manager


def get_jwt_auth() -> JWTAuth:
    """
    Dependency for JWT auth.
    
    Returns:
        JWT auth
    """
    return jwt_auth


def get_current_agent():
    """
    Dependency for current agent.
    
    Returns:
        Current agent dependency
    """
    if jwt_auth:
        return Depends(jwt_auth.requires_auth)
    return Depends(lambda: {"agent_id": "test-agent"}) 