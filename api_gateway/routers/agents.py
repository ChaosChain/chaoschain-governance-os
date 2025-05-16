"""
Agents Router

This module provides the API router for agent operations.
"""

from typing import Dict, List, Optional, Annotated
from pydantic import BaseModel, EmailStr

from fastapi import APIRouter, HTTPException, Depends, status, Query, Path

from api_gateway.dependencies import get_db_adapter
from api_gateway.auth.jwt_auth import create_jwt_token, get_current_agent_id
from api_gateway.metrics import AGENT_REGISTRATIONS, ACTIVE_AGENTS

# Create router
router = APIRouter()


# --- Models ---

class AgentMetadata(BaseModel):
    """Agent metadata model."""
    role: Optional[str] = None
    expertise: Optional[str] = None
    version: Optional[str] = None
    description: Optional[str] = None


class AgentCreate(BaseModel):
    """Agent creation model."""
    name: str
    email: EmailStr
    metadata: Optional[AgentMetadata] = None


class AgentResponse(BaseModel):
    """Agent response model."""
    id: str
    name: str
    email: str
    metadata: Dict[str, str] = {}


class TokenResponse(BaseModel):
    """Token response model."""
    token: str
    agent_id: str


class AgentList(BaseModel):
    """Agent list response model."""
    agents: List[AgentResponse]
    total: int
    limit: int
    offset: int


# --- Routes ---

@router.post("", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register_agent(
    agent: AgentCreate,
    db = Depends(get_db_adapter)
):
    """
    Register a new agent.
    
    Args:
        agent: Agent creation model
        
    Returns:
        TokenResponse with agent ID and JWT token
    """
    try:
        # Convert metadata to dictionary if provided
        metadata = agent.metadata.dict() if agent.metadata else {}
        
        # Register the agent
        agent_id = db.register_agent(
            name=agent.name,
            email=agent.email,
            metadata=metadata
        )
        
        # Create a JWT token for the agent
        token = create_jwt_token(agent_id)
        
        # Update metrics
        AGENT_REGISTRATIONS.inc()
        ACTIVE_AGENTS.inc()
        
        return TokenResponse(
            token=token,
            agent_id=agent_id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register agent: {e}"
        )


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: str = Path(..., description="Agent ID"),
    current_agent_id: str = Depends(get_current_agent_id),
    db = Depends(get_db_adapter)
):
    """
    Get agent by ID.
    
    Args:
        agent_id: Agent ID
        current_agent_id: ID of the authenticated agent
        
    Returns:
        Agent response model
    """
    try:
        agent = db.get_agent(agent_id)
        
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent with ID {agent_id} not found"
            )
        
        return AgentResponse(
            id=agent.get_id(),
            name=agent.get_name(),
            email=agent.get_email(),
            metadata=agent.get_metadata()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get agent: {e}"
        )


@router.get("", response_model=AgentList)
async def list_agents(
    limit: int = Query(10, ge=1, le=100, description="Maximum number of agents to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    current_agent_id: str = Depends(get_current_agent_id),
    db = Depends(get_db_adapter)
):
    """
    List agents with pagination.
    
    Args:
        limit: Maximum number of agents to return
        offset: Offset for pagination
        current_agent_id: ID of the authenticated agent
        
    Returns:
        List of agents
    """
    try:
        # Get agents with pagination
        agents = db.list_agents(limit=limit, offset=offset)
        
        # Convert to response models
        agent_responses = [
            AgentResponse(
                id=agent.get_id(),
                name=agent.get_name(),
                email=agent.get_email(),
                metadata=agent.get_metadata()
            )
            for agent in agents
        ]
        
        # Get total count
        # In a real implementation, we would have a count method
        # For now, we'll just use the length of the returned agents
        total = len(agent_responses)
        
        # Update active agents metric
        ACTIVE_AGENTS.set(total)
        
        return AgentList(
            agents=agent_responses,
            total=total,
            limit=limit,
            offset=offset
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list agents: {e}"
        ) 