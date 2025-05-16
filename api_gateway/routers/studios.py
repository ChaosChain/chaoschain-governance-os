"""
Studios Router for ChaosCore API Gateway

This module provides endpoints for managing studios in the ChaosCore platform.
"""
from typing import Dict, Any, List, Optional, Annotated
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from pydantic import BaseModel, Field

from chaoscore.core.studio import StudioManager
from api_gateway.auth.jwt_auth import JWTAuth
from api_gateway.routers.common import StudioManagerDep, JWTAuthDep, CurrentAgentDep


# Models
class StudioMember(BaseModel):
    """Studio member."""
    agent_id: str = Field(..., description="Agent ID")
    role: str = Field(..., description="Member role")
    permissions: List[str] = Field(default_factory=list, description="Member permissions")


class StudioCreate(BaseModel):
    """Studio creation request."""
    name: str = Field(..., min_length=1, max_length=255, description="Studio name")
    description: str = Field(..., min_length=1, description="Studio description")
    members: List[StudioMember] = Field(default_factory=list, description="Studio members")
    settings: Optional[Dict[str, Any]] = Field(default=None, description="Studio settings")


class StudioResponse(BaseModel):
    """Studio response."""
    id: str = Field(..., description="Studio ID")
    name: str = Field(..., description="Studio name")
    description: str = Field(..., description="Studio description")
    created_at: str = Field(..., description="Creation timestamp")
    owner_id: str = Field(..., description="Owner agent ID")
    members: List[Dict[str, Any]] = Field(default_factory=list, description="Studio members")
    settings: Dict[str, Any] = Field(default_factory=dict, description="Studio settings")


class StudioList(BaseModel):
    """List of studios."""
    studios: List[StudioResponse] = Field(..., description="List of studios")
    total: int = Field(..., description="Total number of studios")
    page: int = Field(..., description="Current page")
    page_size: int = Field(..., description="Page size")


# Router
router = APIRouter()


# Endpoints
@router.post("", response_model=StudioResponse, status_code=201)
async def create_studio(
    studio: StudioCreate,
    manager: StudioManagerDep,
    current_agent: CurrentAgentDep
):
    """
    Create a new studio.
    
    This endpoint creates a new studio in the ChaosCore platform.
    """
    try:
        # Extract agent ID from token
        agent_id = current_agent["agent_id"]
        
        # Convert members to dict
        members = [member.dict() for member in studio.members]
        
        # Convert settings to dict
        settings = studio.settings or {}
        
        # Create the studio
        studio_id = manager.create_studio(
            name=studio.name,
            description=studio.description,
            owner_id=agent_id,
            members=members,
            settings=settings
        )
        
        # Get the created studio
        created_studio = manager.get_studio(studio_id)
        
        if not created_studio:
            raise HTTPException(status_code=500, detail="Failed to retrieve created studio")
        
        # Convert to response model
        return StudioResponse(
            id=created_studio.get_id(),
            name=created_studio.get_name(),
            description=created_studio.get_description(),
            created_at=created_studio.get_created_at(),
            owner_id=created_studio.get_owner_id(),
            members=created_studio.get_members(),
            settings=created_studio.get_settings()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create studio: {str(e)}")


@router.get("", response_model=StudioList)
async def list_studios(
    manager: StudioManagerDep,
    current_agent: CurrentAgentDep,
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Page size")
):
    """
    List studios.
    
    This endpoint retrieves a list of studios in the ChaosCore platform.
    """
    try:
        # Extract agent ID from token
        agent_id = current_agent["agent_id"]
        
        # Calculate offset
        offset = (page - 1) * page_size
        
        # Get studios
        studios = manager.list_studios(agent_id=agent_id, limit=page_size, offset=offset)
        
        # Convert to response model
        studio_responses = []
        for studio in studios:
            studio_responses.append(StudioResponse(
                id=studio.get_id(),
                name=studio.get_name(),
                description=studio.get_description(),
                created_at=studio.get_created_at(),
                owner_id=studio.get_owner_id(),
                members=studio.get_members(),
                settings=studio.get_settings()
            ))
        
        # Return list
        return StudioList(
            studios=studio_responses,
            total=len(studio_responses),  # This is not accurate, but we don't have a count method
            page=page,
            page_size=page_size
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list studios: {str(e)}")


@router.get("/{studio_id}", response_model=StudioResponse)
async def get_studio(
    studio_id: str,
    manager: StudioManagerDep,
    current_agent: CurrentAgentDep
):
    """
    Get a studio.
    
    This endpoint retrieves a studio by ID.
    """
    try:
        # Get the studio
        studio = manager.get_studio(studio_id)
        
        if not studio:
            raise HTTPException(status_code=404, detail=f"Studio not found: {studio_id}")
        
        # Check if the agent is a member of the studio
        agent_id = current_agent["agent_id"]
        members = studio.get_members()
        
        is_member = False
        for member in members:
            if member.get("agent_id") == agent_id:
                is_member = True
                break
        
        if not is_member and studio.get_owner_id() != agent_id:
            raise HTTPException(status_code=403, detail="You are not a member of this studio")
        
        # Convert to response model
        return StudioResponse(
            id=studio.get_id(),
            name=studio.get_name(),
            description=studio.get_description(),
            created_at=studio.get_created_at(),
            owner_id=studio.get_owner_id(),
            members=studio.get_members(),
            settings=studio.get_settings()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get studio: {str(e)}")


@router.post("/{studio_id}/members", response_model=StudioResponse)
async def add_member(
    member: StudioMember,
    studio_id: str,
    manager: StudioManagerDep,
    current_agent: CurrentAgentDep
):
    """
    Add a member to a studio.
    
    This endpoint adds a member to a studio in the ChaosCore platform.
    """
    try:
        # Get the studio
        studio = manager.get_studio(studio_id)
        
        if not studio:
            raise HTTPException(status_code=404, detail=f"Studio not found: {studio_id}")
        
        # Check if the agent is the owner of the studio
        agent_id = current_agent["agent_id"]
        
        if studio.get_owner_id() != agent_id:
            raise HTTPException(status_code=403, detail="Only the studio owner can add members")
        
        # Add the member
        success = manager.add_studio_member(
            studio_id=studio_id,
            agent_id=member.agent_id,
            role=member.role,
            permissions=member.permissions
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to add member to studio")
        
        # Get the updated studio
        updated_studio = manager.get_studio(studio_id)
        
        # Convert to response model
        return StudioResponse(
            id=updated_studio.get_id(),
            name=updated_studio.get_name(),
            description=updated_studio.get_description(),
            created_at=updated_studio.get_created_at(),
            owner_id=updated_studio.get_owner_id(),
            members=updated_studio.get_members(),
            settings=updated_studio.get_settings()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add member to studio: {str(e)}")


@router.delete("/{studio_id}/members/{agent_id}", response_model=StudioResponse)
async def remove_member(
    studio_id: str,
    agent_id: str,
    manager: StudioManagerDep,
    current_agent: CurrentAgentDep
):
    """
    Remove a member from a studio.
    
    This endpoint removes a member from a studio in the ChaosCore platform.
    """
    try:
        # Get the studio
        studio = manager.get_studio(studio_id)
        
        if not studio:
            raise HTTPException(status_code=404, detail=f"Studio not found: {studio_id}")
        
        # Check if the agent is the owner of the studio
        current_agent_id = current_agent["agent_id"]
        
        if studio.get_owner_id() != current_agent_id:
            raise HTTPException(status_code=403, detail="Only the studio owner can remove members")
        
        # Remove the member
        success = manager.remove_studio_member(studio_id=studio_id, agent_id=agent_id)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to remove member from studio")
        
        # Get the updated studio
        updated_studio = manager.get_studio(studio_id)
        
        # Convert to response model
        return StudioResponse(
            id=updated_studio.get_id(),
            name=updated_studio.get_name(),
            description=updated_studio.get_description(),
            created_at=updated_studio.get_created_at(),
            owner_id=updated_studio.get_owner_id(),
            members=updated_studio.get_members(),
            settings=updated_studio.get_settings()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove member from studio: {str(e)}") 