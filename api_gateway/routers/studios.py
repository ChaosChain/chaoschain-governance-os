"""
Studios Router

This module provides the API router for studio operations.
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

from fastapi import APIRouter, HTTPException, Depends, status, Query, Path

from api_gateway.dependencies import get_db_adapter
from api_gateway.auth.jwt_auth import get_current_agent_id
from api_gateway.metrics import STUDIOS_CREATED, TASKS_CREATED

# Create router
router = APIRouter()


# --- Models ---

class StudioMetadata(BaseModel):
    """Studio metadata model."""
    domain: Optional[str] = None
    version: Optional[str] = None
    tags: Optional[List[str]] = None


class StudioCreate(BaseModel):
    """Studio creation model."""
    name: str = Field(..., description="Name of the studio")
    description: str = Field(..., description="Description of the studio")
    metadata: Optional[StudioMetadata] = None


class StudioResponse(BaseModel):
    """Studio response model."""
    id: str
    name: str
    description: str
    owner_id: str
    metadata: Dict[str, Any] = {}
    created_at: str


class StudioList(BaseModel):
    """Studio list response model."""
    studios: List[StudioResponse]
    total: int
    limit: int
    offset: int


class TaskCreate(BaseModel):
    """Task creation model."""
    name: str = Field(..., description="Name of the task")
    description: str = Field(..., description="Description of the task")
    parameters: Dict[str, Any] = Field({}, description="Task parameters")


class TaskResponse(BaseModel):
    """Task response model."""
    id: str
    studio_id: str
    name: str
    description: str
    parameters: Dict[str, Any] = {}
    status: str
    created_at: str
    updated_at: str


# --- Routes ---

@router.post("", response_model=StudioResponse, status_code=status.HTTP_201_CREATED)
async def create_studio(
    studio: StudioCreate,
    current_agent_id: str = Depends(get_current_agent_id),
    db = Depends(get_db_adapter)
):
    """
    Create a new studio.
    
    Args:
        studio: Studio creation model
        current_agent_id: ID of the authenticated agent (studio owner)
        
    Returns:
        StudioResponse with studio details
    """
    try:
        # Convert metadata to dictionary if provided
        metadata = studio.metadata.dict() if studio.metadata else {}
        
        # Create the studio
        studio_id = db.create_studio(
            name=studio.name,
            description=studio.description,
            owner_id=current_agent_id,
            metadata=metadata
        )
        
        # Update metrics
        STUDIOS_CREATED.inc()
        
        # Get the created studio
        created_studio = db.get_studio(studio_id)
        
        return StudioResponse(
            id=created_studio.get_id(),
            name=created_studio.get_name(),
            description=created_studio.get_description(),
            owner_id=created_studio.get_owner_id(),
            metadata=created_studio.get_metadata(),
            created_at=created_studio.get_created_at().isoformat()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create studio: {e}"
        )


@router.get("/{studio_id}", response_model=StudioResponse)
async def get_studio(
    studio_id: str = Path(..., description="Studio ID"),
    current_agent_id: str = Depends(get_current_agent_id),
    db = Depends(get_db_adapter)
):
    """
    Get studio by ID.
    
    Args:
        studio_id: Studio ID
        current_agent_id: ID of the authenticated agent
        
    Returns:
        Studio response model
    """
    try:
        studio = db.get_studio(studio_id)
        
        if not studio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Studio with ID {studio_id} not found"
            )
        
        return StudioResponse(
            id=studio.get_id(),
            name=studio.get_name(),
            description=studio.get_description(),
            owner_id=studio.get_owner_id(),
            metadata=studio.get_metadata(),
            created_at=studio.get_created_at().isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get studio: {e}"
        )


@router.get("", response_model=StudioList)
async def list_studios(
    limit: int = Query(10, ge=1, le=100, description="Maximum number of studios to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    current_agent_id: str = Depends(get_current_agent_id),
    db = Depends(get_db_adapter)
):
    """
    List studios with pagination.
    
    Args:
        limit: Maximum number of studios to return
        offset: Offset for pagination
        current_agent_id: ID of the authenticated agent
        
    Returns:
        List of studios
    """
    try:
        # Get studios with pagination
        studios = db.list_studios(limit=limit, offset=offset)
        
        # Convert to response models
        studio_responses = [
            StudioResponse(
                id=studio.get_id(),
                name=studio.get_name(),
                description=studio.get_description(),
                owner_id=studio.get_owner_id(),
                metadata=studio.get_metadata(),
                created_at=studio.get_created_at().isoformat()
            )
            for studio in studios
        ]
        
        # Get total count
        # In a real implementation, we would have a count method
        # For now, we'll just use the length of the returned studios
        total = len(studio_responses)
        
        return StudioList(
            studios=studio_responses,
            total=total,
            limit=limit,
            offset=offset
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list studios: {e}"
        )


@router.post("/{studio_id}/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task: TaskCreate,
    studio_id: str = Path(..., description="Studio ID"),
    current_agent_id: str = Depends(get_current_agent_id),
    db = Depends(get_db_adapter)
):
    """
    Create a new task in a studio.
    
    Args:
        task: Task creation model
        studio_id: Studio ID
        current_agent_id: ID of the authenticated agent
        
    Returns:
        TaskResponse with task details
    """
    try:
        # Check if studio exists and the current agent is the owner
        studio = db.get_studio(studio_id)
        
        if not studio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Studio with ID {studio_id} not found"
            )
        
        if studio.get_owner_id() != current_agent_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the studio owner can create tasks"
            )
        
        # Create the task
        task_id = db.create_task(
            studio_id=studio_id,
            name=task.name,
            description=task.description,
            parameters=task.parameters
        )
        
        # Update metrics
        TASKS_CREATED.inc()
        
        # Get the created task
        created_task = db.get_task(task_id)
        
        return TaskResponse(
            id=created_task.get_id(),
            studio_id=created_task.get_studio_id(),
            name=created_task.get_name(),
            description=created_task.get_description(),
            parameters=created_task.get_parameters(),
            status=created_task.get_status(),
            created_at=created_task.get_created_at().isoformat(),
            updated_at=created_task.get_updated_at().isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create task: {e}"
        ) 