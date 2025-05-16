"""
Actions Router for ChaosCore API Gateway

This module provides endpoints for managing actions in the ChaosCore platform.
"""
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from pydantic import BaseModel, Field

from chaoscore.core.proof_of_agency import ProofOfAgencyInterface
from api_gateway.auth.jwt_auth import JWTAuth


# Models
class ActionData(BaseModel):
    """Action data."""
    proposal_id: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    context: Optional[Dict[str, Any]] = None


class ActionCreate(BaseModel):
    """Action creation request."""
    action_type: str = Field(..., min_length=1, max_length=255, description="Action type")
    description: str = Field(..., min_length=1, description="Action description")
    data: Optional[ActionData] = Field(default=None, description="Action data")


class OutcomeResults(BaseModel):
    """Outcome results."""
    proposal_result: Optional[Dict[str, Any]] = None
    simulation: Optional[Dict[str, Any]] = None
    metrics: Optional[Dict[str, Any]] = None


class OutcomeCreate(BaseModel):
    """Outcome creation request."""
    success: bool = Field(..., description="Whether the action was successful")
    results: Optional[OutcomeResults] = Field(default=None, description="Outcome results")
    impact_score: float = Field(0.0, ge=0.0, le=1.0, description="Impact score of the action")


class ActionResponse(BaseModel):
    """Action response."""
    id: str = Field(..., description="Action ID")
    agent_id: str = Field(..., description="Agent ID")
    action_type: str = Field(..., description="Action type")
    description: str = Field(..., description="Action description")
    timestamp: str = Field(..., description="Action timestamp")
    data: Optional[Dict[str, Any]] = Field(default={}, description="Action data")
    anchored: bool = Field(False, description="Whether the action is anchored on blockchain")
    tx_hash: Optional[str] = Field(None, description="Transaction hash if anchored")
    outcome: Optional[Dict[str, Any]] = Field(None, description="Action outcome")


class ActionList(BaseModel):
    """List of actions."""
    actions: List[ActionResponse] = Field(..., description="List of actions")
    total: int = Field(..., description="Total number of actions")
    page: int = Field(..., description="Current page")
    page_size: int = Field(..., description="Page size")


# Router
router = APIRouter()


# Dependencies
def get_proof_of_agency(poa: ProofOfAgencyInterface = Depends()) -> ProofOfAgencyInterface:
    """Get the proof of agency."""
    return poa


def get_jwt_auth(auth: JWTAuth = Depends()) -> JWTAuth:
    """Get the JWT authentication handler."""
    return auth


# Endpoints
@router.post("", response_model=ActionResponse, status_code=201)
async def create_action(
    action: ActionCreate,
    poa: ProofOfAgencyInterface = Depends(get_proof_of_agency),
    current_agent: Dict[str, Any] = Depends(JWTAuth.requires_auth)
):
    """
    Log an action.
    
    This endpoint logs an action in the ChaosCore platform.
    """
    try:
        # Extract agent ID from token
        agent_id = current_agent["agent_id"]
        
        # Convert data model to dict
        data = action.data.dict() if action.data else {}
        
        # Filter out None values
        data = {k: v for k, v in data.items() if v is not None}
        
        # Log the action
        action_id = poa.log_action(
            agent_id=agent_id,
            action_type=action.action_type,
            description=action.description,
            data=data
        )
        
        # Get the action (not available in the interface, so we'll mock it)
        result = {
            "id": action_id,
            "agent_id": agent_id,
            "action_type": action.action_type,
            "description": action.description,
            "timestamp": "now",  # This would be retrieved from the actual action
            "data": data,
            "anchored": False,
            "tx_hash": None,
            "outcome": None
        }
        
        return ActionResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to log action: {str(e)}")


@router.post("/{action_id}/outcome", response_model=ActionResponse)
async def record_outcome(
    outcome: OutcomeCreate,
    action_id: str = Path(..., description="Action ID"),
    poa: ProofOfAgencyInterface = Depends(get_proof_of_agency),
    current_agent: Dict[str, Any] = Depends(JWTAuth.requires_auth)
):
    """
    Record an action outcome.
    
    This endpoint records the outcome of an action in the ChaosCore platform.
    """
    try:
        # Convert results model to dict
        results = outcome.results.dict() if outcome.results else {}
        
        # Filter out None values
        results = {k: v for k, v in results.items() if v is not None}
        
        # Record the outcome
        success = poa.record_outcome(
            action_id=action_id,
            success=outcome.success,
            results=results,
            impact_score=outcome.impact_score
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to record outcome")
        
        # Get the action (not available in the interface, so we'll mock it)
        result = {
            "id": action_id,
            "agent_id": current_agent["agent_id"],  # This would be retrieved from the actual action
            "action_type": "unknown",  # This would be retrieved from the actual action
            "description": "unknown",  # This would be retrieved from the actual action
            "timestamp": "now",  # This would be retrieved from the actual action
            "data": {},  # This would be retrieved from the actual action
            "anchored": False,
            "tx_hash": None,
            "outcome": {
                "success": outcome.success,
                "results": results,
                "impact_score": outcome.impact_score,
                "timestamp": "now",  # This would be retrieved from the actual outcome
                "anchored": False,
                "tx_hash": None
            }
        }
        
        return ActionResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to record outcome: {str(e)}")


@router.get("", response_model=ActionList)
async def list_actions(
    agent_id: Optional[str] = Query(None, description="Filter by agent ID"),
    action_type: Optional[str] = Query(None, description="Filter by action type"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Page size"),
    poa: ProofOfAgencyInterface = Depends(get_proof_of_agency),
    current_agent: Dict[str, Any] = Depends(JWTAuth.requires_auth)
):
    """
    List actions.
    
    This endpoint retrieves a list of actions from the ChaosCore platform.
    """
    # This is a simplified implementation since the current interface doesn't support querying
    # In a real implementation, we would use a method like poa.list_actions()
    return ActionList(
        actions=[],
        total=0,
        page=page,
        page_size=page_size
    )


@router.get("/{action_id}", response_model=ActionResponse)
async def get_action(
    action_id: str = Path(..., description="Action ID"),
    poa: ProofOfAgencyInterface = Depends(get_proof_of_agency),
    current_agent: Dict[str, Any] = Depends(JWTAuth.requires_auth)
):
    """
    Get an action.
    
    This endpoint retrieves an action by ID.
    """
    # This is a simplified implementation since the current interface doesn't support getting an action
    # In a real implementation, we would use a method like poa.get_action()
    raise HTTPException(status_code=404, detail=f"Action not found: {action_id}") 