"""
Agents router for the ChaosCore API Gateway.

This module provides endpoints for managing agents.
"""

import uuid
from typing import Dict, Any, List, Optional, Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, EmailStr

from chaoscore.core.agent_registry import AgentRegistryInterface
from api_gateway.auth.jwt_auth import JWTAuth
from api_gateway.routers.common import RegistryDep, JWTAuthDep, CurrentAgentDep


class AgentCreate(BaseModel):
    """Agent creation model."""
    name: str = Field(..., description="Agent name")
    email: Optional[EmailStr] = Field(None, description="Agent email")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Agent metadata")


class AgentUpdate(BaseModel):
    """Agent update model."""
    name: Optional[str] = Field(None, description="Agent name")
    email: Optional[EmailStr] = Field(None, description="Agent email")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Agent metadata")


class AgentResponse(BaseModel):
    """Agent response model."""
    id: str = Field(..., description="Agent ID")
    name: str = Field(..., description="Agent name")
    email: Optional[str] = Field(None, description="Agent email")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Agent metadata")


class AgentListResponse(BaseModel):
    """Agent list response model."""
    agents: List[AgentResponse] = Field(..., description="List of agents")
    total: int = Field(..., description="Total number of agents")
    page: int = Field(..., description="Current page")
    page_size: int = Field(..., description="Page size")


# Create router
router = APIRouter()


@router.post("", response_model=AgentResponse, status_code=201)
async def create_agent(
    agent: AgentCreate,
    agent_registry: RegistryDep
):
    """
    Create a new agent.
    
    Args:
        agent: Agent creation data
        agent_registry: Agent registry
        
    Returns:
        Created agent
    """
    agent_id = f"agent-{uuid.uuid4()}"
    agent_registry.create_agent(
        agent_id=agent_id,
        name=agent.name,
        email=agent.email,
        metadata=agent.metadata
    )
    
    # Get the created agent
    created_agent = agent_registry.get_agent(agent_id)
    if not created_agent:
        raise HTTPException(status_code=500, detail="Failed to create agent")
    
    return created_agent


@router.get("", response_model=AgentListResponse)
async def list_agents(
    agent_registry: RegistryDep,
    auth: JWTAuthDep,
    page: int = 1,
    page_size: int = 10
):
    """
    List agents.
    
    Args:
        agent_registry: Agent registry
        auth: JWT auth
        page: Page number
        page_size: Page size
        
    Returns:
        List of agents
    """
    # Calculate offset
    offset = (page - 1) * page_size
    
    # Get agents
    agents = agent_registry.list_agents(
        limit=page_size,
        offset=offset
    )
    
    # Get total count (in a real implementation, this would be a separate database query)
    total = len(agents) + offset  # This is just a simple approximation
    
    return {
        "agents": agents,
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.get("/me", response_model=AgentResponse)
async def get_current_agent(
    current_agent: CurrentAgentDep,
    agent_registry: RegistryDep
):
    """
    Get the current authenticated agent.
    
    Args:
        current_agent: Current agent from JWT auth
        agent_registry: Agent registry
        
    Returns:
        Current agent
    """
    agent_id = current_agent["agent_id"]
    agent = agent_registry.get_agent(agent_id)
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return agent


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: str,
    agent_registry: RegistryDep,
    auth: JWTAuthDep
):
    """
    Get an agent by ID.
    
    Args:
        agent_id: Agent ID
        agent_registry: Agent registry
        auth: JWT auth
        
    Returns:
        Agent
    """
    agent = agent_registry.get_agent(agent_id)
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return agent


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: str,
    agent_update: AgentUpdate,
    agent_registry: RegistryDep,
    current_agent: CurrentAgentDep
):
    """
    Update an agent.
    
    Args:
        agent_id: Agent ID
        agent_update: Agent update data
        agent_registry: Agent registry
        current_agent: Current agent from JWT auth
        
    Returns:
        Updated agent
    """
    # Check if the agent exists
    existing_agent = agent_registry.get_agent(agent_id)
    if not existing_agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Check if the current agent is updating itself
    if current_agent["agent_id"] != agent_id:
        raise HTTPException(status_code=403, detail="You can only update your own agent")
    
    # Update the agent
    success = agent_registry.update_agent(
        agent_id=agent_id,
        name=agent_update.name,
        email=agent_update.email,
        metadata=agent_update.metadata
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update agent")
    
    # Get the updated agent
    updated_agent = agent_registry.get_agent(agent_id)
    
    return updated_agent 