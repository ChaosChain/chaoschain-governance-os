"""
Reputation Router

This module provides the API router for reputation operations.
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

from fastapi import APIRouter, HTTPException, Depends, status, Query, Path

from api_gateway.dependencies import get_db_adapter
from api_gateway.auth.jwt_auth import get_current_agent_id
from api_gateway.metrics import REPUTATION_QUERIES

# Create router
router = APIRouter()


# --- Models ---

class ReputationResponse(BaseModel):
    """Reputation response model."""
    agent_id: str
    score: float
    rank: Optional[int] = None
    components: Dict[str, float] = {}
    last_updated: str


class ReputationList(BaseModel):
    """Reputation list response model."""
    reputations: List[ReputationResponse]
    total: int
    limit: int
    offset: int


# --- Routes ---

@router.get("/agents/{agent_id}", response_model=ReputationResponse)
async def get_agent_reputation(
    agent_id: str = Path(..., description="Agent ID"),
    current_agent_id: str = Depends(get_current_agent_id),
    db = Depends(get_db_adapter)
):
    """
    Get reputation for an agent.
    
    Args:
        agent_id: Agent ID
        current_agent_id: ID of the authenticated agent
        
    Returns:
        ReputationResponse with reputation details
    """
    try:
        # Check if agent exists
        agent = db.get_agent(agent_id)
        
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent with ID {agent_id} not found"
            )
        
        # Update metrics
        REPUTATION_QUERIES.inc()
        
        # Get reputation
        reputation = db.get_agent_reputation(agent_id)
        
        if not reputation:
            # If no reputation exists, return default values
            return ReputationResponse(
                agent_id=agent_id,
                score=0.0,
                rank=None,
                components={},
                last_updated=agent.get_registration_time().isoformat()
            )
        
        return ReputationResponse(
            agent_id=agent_id,
            score=reputation.get_score(),
            rank=reputation.get_rank(),
            components=reputation.get_components(),
            last_updated=reputation.get_last_updated().isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get agent reputation: {e}"
        )


@router.get("/agents", response_model=ReputationList)
async def list_agent_reputations(
    limit: int = Query(10, ge=1, le=100, description="Maximum number of reputations to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    min_score: Optional[float] = Query(None, ge=0.0, le=1.0, description="Minimum reputation score"),
    domain: Optional[str] = Query(None, description="Reputation domain filter"),
    current_agent_id: str = Depends(get_current_agent_id),
    db = Depends(get_db_adapter)
):
    """
    List agent reputations with pagination and filtering.
    
    Args:
        limit: Maximum number of reputations to return
        offset: Offset for pagination
        min_score: Minimum reputation score filter
        domain: Reputation domain filter
        current_agent_id: ID of the authenticated agent
        
    Returns:
        List of agent reputations
    """
    try:
        # Update metrics
        REPUTATION_QUERIES.inc()
        
        # Get agent reputations with pagination and filtering
        reputations = db.list_agent_reputations(
            limit=limit,
            offset=offset,
            min_score=min_score,
            domain=domain
        )
        
        # Convert to response models
        reputation_responses = [
            ReputationResponse(
                agent_id=rep.get_agent_id(),
                score=rep.get_score(),
                rank=rep.get_rank(),
                components=rep.get_components(),
                last_updated=rep.get_last_updated().isoformat()
            )
            for rep in reputations
        ]
        
        # Get total count
        # In a real implementation, we would have a count method
        # For now, we'll just use the length of the returned reputations
        total = len(reputation_responses)
        
        return ReputationList(
            reputations=reputation_responses,
            total=total,
            limit=limit,
            offset=offset
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list agent reputations: {e}"
        )


@router.get("/domains/{domain}", response_model=ReputationList)
async def get_domain_reputation_leaderboard(
    domain: str = Path(..., description="Reputation domain"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of agents to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    current_agent_id: str = Depends(get_current_agent_id),
    db = Depends(get_db_adapter)
):
    """
    Get reputation leaderboard for a specific domain.
    
    Args:
        domain: Reputation domain
        limit: Maximum number of agents to return
        offset: Offset for pagination
        current_agent_id: ID of the authenticated agent
        
    Returns:
        List of agent reputations for the domain
    """
    try:
        # Update metrics
        REPUTATION_QUERIES.inc()
        
        # Get domain reputation leaderboard
        reputations = db.get_domain_reputation_leaderboard(
            domain=domain,
            limit=limit,
            offset=offset
        )
        
        # Convert to response models
        reputation_responses = [
            ReputationResponse(
                agent_id=rep.get_agent_id(),
                score=rep.get_score(),
                rank=rep.get_rank(),
                components=rep.get_components(),
                last_updated=rep.get_last_updated().isoformat()
            )
            for rep in reputations
        ]
        
        # Get total count
        # In a real implementation, we would have a count method
        # For now, we'll just use the length of the returned reputations
        total = len(reputation_responses)
        
        return ReputationList(
            reputations=reputation_responses,
            total=total,
            limit=limit,
            offset=offset
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get domain reputation leaderboard: {e}"
        ) 