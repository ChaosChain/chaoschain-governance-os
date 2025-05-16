"""
Actions Router

This module provides the API router for action operations.
"""

from typing import Dict, List, Optional, Any, Annotated
from datetime import datetime
from pydantic import BaseModel, Field, RootModel

from fastapi import APIRouter, HTTPException, Depends, status, Query, Path

from api_gateway.dependencies import get_db_adapter
from api_gateway.auth.jwt_auth import get_current_agent_id
from api_gateway.metrics import ACTIONS_LOGGED, OUTCOMES_RECORDED

# Create router
router = APIRouter()


# --- Models ---

class ActionData(RootModel):
    """Action data model."""
    root: Dict[str, Any]


class ActionCreate(BaseModel):
    """Action creation model."""
    action_type: str = Field(..., description="Type of action (e.g., PROPOSE, REVIEW)")
    description: str = Field(..., description="Description of the action")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional action data")


class ActionResponse(BaseModel):
    """Action response model."""
    id: str
    agent_id: str
    action_type: str
    description: str
    data: Dict[str, Any] = {}
    timestamp: str


class OutcomeData(RootModel):
    """Outcome data model."""
    root: Dict[str, Any]


class OutcomeCreate(BaseModel):
    """Outcome creation model."""
    success: bool = Field(..., description="Whether the action was successful")
    results: Optional[Dict[str, Any]] = Field(None, description="Action results")
    impact_score: float = Field(0.0, ge=0.0, le=1.0, description="Impact score of the action")


class OutcomeResponse(BaseModel):
    """Outcome response model."""
    action_id: str
    success: bool
    results: Dict[str, Any] = {}
    impact_score: float
    timestamp: str


# --- Routes ---

@router.post("", response_model=ActionResponse, status_code=status.HTTP_201_CREATED)
async def log_action(
    action: ActionCreate,
    current_agent_id: str = Depends(get_current_agent_id),
    db = Depends(get_db_adapter)
):
    """
    Log an action.
    
    Args:
        action: Action creation model
        current_agent_id: ID of the authenticated agent
        
    Returns:
        ActionResponse with action details
    """
    try:
        # Log the action
        action_id = db.log_action(
            agent_id=current_agent_id,
            action_type=action.action_type,
            description=action.description,
            data=action.data
        )
        
        # Update metrics
        ACTIONS_LOGGED.labels(action_type=action.action_type).inc()
        
        # Return a simulated response
        # In a real implementation, we would fetch the action from the database
        return ActionResponse(
            id=action_id,
            agent_id=current_agent_id,
            action_type=action.action_type,
            description=action.description,
            data=action.data or {},
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to log action: {e}"
        )


@router.post("/{action_id}/outcomes", response_model=OutcomeResponse, status_code=status.HTTP_201_CREATED)
async def record_outcome(
    outcome: OutcomeCreate,
    action_id: str = Path(..., description="Action ID"),
    current_agent_id: str = Depends(get_current_agent_id),
    db = Depends(get_db_adapter)
):
    """
    Record the outcome of an action.
    
    Args:
        outcome: Outcome creation model
        action_id: Action ID
        current_agent_id: ID of the authenticated agent
        
    Returns:
        OutcomeResponse with outcome details
    """
    try:
        # Record the outcome
        success = db.record_outcome(
            action_id=action_id,
            success=outcome.success,
            results=outcome.results,
            impact_score=outcome.impact_score
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to record outcome"
            )
        
        # Update metrics
        OUTCOMES_RECORDED.labels(success="true" if outcome.success else "false").inc()
        
        # Return a simulated response
        # In a real implementation, we would fetch the outcome from the database
        return OutcomeResponse(
            action_id=action_id,
            success=outcome.success,
            results=outcome.results or {},
            impact_score=outcome.impact_score,
            timestamp=datetime.now().isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record outcome: {e}"
        ) 