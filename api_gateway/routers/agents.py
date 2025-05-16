"""
Agents Router for ChaosCore API Gateway

This module provides endpoints for managing agents in the ChaosCore platform.
"""
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from pydantic import BaseModel, Field, EmailStr

from chaoscore.core.agent_registry import AgentRegistryInterface
from api_gateway.auth.jwt_auth import JWTAuth


# Models
class AgentMetadata(BaseModel):
    """Agent metadata."""
    role: Optional[str] = None
    expertise: Optional[str] = None
    public_key: Optional[str] = None
    version: Optional[str] = None
    capabilities: Optional[List[str]] = None


class AgentCreate(BaseModel):
    """Agent creation request."""
    name: str = Field(..., min_length=1, max_length=255, description="Agent name")
    email: EmailStr = Field(..., description="Agent email")
    metadata: Optional[AgentMetadata] = Field(default=None, description="Agent metadata")


class AgentResponse(BaseModel):
    """Agent response."""
    id: str = Field(..., description="Agent ID")
    name: str = Field(..., description="Agent name")
    email: str = Field(..., description="Agent email")
    created_at: Optional[str] = Field(None, description="Creation timestamp")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="Agent metadata")


class AgentList(BaseModel):
    """List of agents."""
    agents: List[AgentResponse] = Field(..., description="List of agents")
    total: int = Field(..., description="Total number of agents")
    page: int = Field(..., description="Current page")
    page_size: int = Field(..., description="Page size")


# Router
router = APIRouter()


# Dependencies
def get_agent_registry(registry: AgentRegistryInterface = Depends()) -> AgentRegistryInterface:
    """Get the agent registry."""
    return registry


def get_jwt_auth(auth: JWTAuth = Depends()) -> JWTAuth:
    """Get the JWT authentication handler."""
    return auth


# Endpoints
@router.post("", response_model=AgentResponse, status_code=201)
async def create_agent(
    agent: AgentCreate,
    registry: AgentRegistryInterface = Depends(get_agent_registry)
):
    """
    Create a new agent.
    
    This endpoint registers a new agent in the ChaosCore platform.
    """
    metadata = agent.metadata.dict() if agent.metadata else {}
    
    # Filter out None values
    metadata = {k: v for k, v in metadata.items() if v is not None}
    
    try:
        agent_id = registry.register_agent(
            name=agent.name,
            email=agent.email,
            metadata=metadata
        )
        
        # Get the created agent
        created_agent = registry.get_agent(agent_id)
        
        if not created_agent:
            raise HTTPException(status_code=500, detail="Failed to retrieve created agent")
        
        # Convert to response model
        return AgentResponse(
            id=created_agent.get_id(),
            name=created_agent.get_name(),
            email=created_agent.get_email(),
            metadata=created_agent.get_metadata()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create agent: {str(e)}")


@router.get("", response_model=AgentList)
async def list_agents(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Page size"),
    registry: AgentRegistryInterface = Depends(get_agent_registry),
    current_agent: Dict[str, Any] = Depends(JWTAuth.requires_auth)
):
    """
    List agents.
    
    This endpoint retrieves a list of agents registered in the ChaosCore platform.
    """
    try:
        # Calculate offset
        offset = (page - 1) * page_size
        
        # Get agents
        agents = registry.list_agents(limit=page_size, offset=offset)
        
        # Convert to response model
        agent_responses = []
        for agent in agents:
            agent_responses.append(AgentResponse(
                id=agent.get_id(),
                name=agent.get_name(),
                email=agent.get_email(),
                metadata=agent.get_metadata()
            ))
        
        # Return list
        return AgentList(
            agents=agent_responses,
            total=len(agents),  # This is not accurate, but we don't have a count method
            page=page,
            page_size=page_size
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list agents: {str(e)}")


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: str = Path(..., description="Agent ID"),
    registry: AgentRegistryInterface = Depends(get_agent_registry),
    current_agent: Dict[str, Any] = Depends(JWTAuth.requires_auth)
):
    """
    Get an agent.
    
    This endpoint retrieves an agent by ID.
    """
    try:
        agent = registry.get_agent(agent_id)
        
        if not agent:
            raise HTTPException(status_code=404, detail=f"Agent not found: {agent_id}")
        
        # Convert to response model
        return AgentResponse(
            id=agent.get_id(),
            name=agent.get_name(),
            email=agent.get_email(),
            metadata=agent.get_metadata()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get agent: {str(e)}")


@router.get("/me", response_model=AgentResponse)
async def get_current_agent(
    current_agent: Dict[str, Any] = Depends(JWTAuth.requires_auth)
):
    """
    Get the current agent.
    
    This endpoint retrieves the current authenticated agent.
    """
    return AgentResponse(
        id=current_agent["agent_id"],
        name=current_agent["name"],
        email=current_agent["email"],
        metadata=current_agent["metadata"]
    ) 