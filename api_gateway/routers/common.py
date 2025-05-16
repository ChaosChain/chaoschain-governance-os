"""
Common dependencies for routers.
"""
from typing import Dict, Any, Annotated
from fastapi import Depends

from api_gateway.auth.jwt_auth import JWTAuth
from chaoscore.core.agent_registry import AgentRegistryInterface
from chaoscore.core.proof_of_agency import ProofOfAgencyInterface
from chaoscore.core.reputation import ReputationSystem
from chaoscore.core.studio import StudioManager
from api_gateway.dependencies import get_agent_registry, get_proof_of_agency, get_reputation_system, get_studio_manager, get_jwt_auth

# Define dependencies using Annotated
RegistryDep = Annotated[AgentRegistryInterface, Depends(get_agent_registry)]
PoADep = Annotated[ProofOfAgencyInterface, Depends(get_proof_of_agency)]
ReputationSystemDep = Annotated[ReputationSystem, Depends(get_reputation_system)]
StudioManagerDep = Annotated[StudioManager, Depends(get_studio_manager)]
JWTAuthDep = Annotated[JWTAuth, Depends(get_jwt_auth)]

# For current agent, we can't use the get_current_agent from dependencies directly
# because it would cause a circular import, so we redefine it here
def get_current_agent():
    auth = get_jwt_auth()
    if auth:
        return auth.requires_auth
    # Fallback for tests
    return lambda: {"agent_id": "test-agent"}

CurrentAgentDep = Annotated[Dict[str, Any], Depends(get_current_agent())] 