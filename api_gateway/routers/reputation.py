"""
Reputation Router for ChaosCore API Gateway

This module provides endpoints for interacting with the reputation system in the ChaosCore platform.
"""
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from pydantic import BaseModel, Field

from chaoscore.core.reputation import ReputationSystem
from api_gateway.auth.jwt_auth import JWTAuth


# Models
class ReputationScore(BaseModel):
    """Reputation score."""
    agent_id: str = Field(..., description="Agent ID")
    score: float = Field(..., description="Reputation score")
    category: Optional[str] = Field(None, description="Reputation category")
    updated_at: str = Field(..., description="Last update timestamp")


class ReputationHistory(BaseModel):
    """Reputation history entry."""
    agent_id: str = Field(..., description="Agent ID")
    score: float = Field(..., description="Reputation score")
    category: Optional[str] = Field(None, description="Reputation category")
    timestamp: str = Field(..., description="Timestamp")
    reason: Optional[str] = Field(None, description="Reason for score change")
    action_id: Optional[str] = Field(None, description="Related action ID")


class ReputationHistoryList(BaseModel):
    """List of reputation history entries."""
    history: List[ReputationHistory] = Field(..., description="Reputation history")
    total: int = Field(..., description="Total number of entries")
    page: int = Field(..., description="Current page")
    page_size: int = Field(..., description="Page size")


class ReputationUpdate(BaseModel):
    """Reputation update request."""
    score_delta: float = Field(..., description="Score delta (positive or negative)")
    category: Optional[str] = Field(None, description="Reputation category")
    reason: str = Field(..., min_length=1, description="Reason for score change")
    action_id: Optional[str] = Field(None, description="Related action ID")


# Router
router = APIRouter()


# Dependencies
def get_reputation_system(system: ReputationSystem = Depends()) -> ReputationSystem:
    """Get the reputation system."""
    return system


def get_jwt_auth(auth: JWTAuth = Depends()) -> JWTAuth:
    """Get the JWT authentication handler."""
    return auth


# Endpoints
@router.get("/agents/{agent_id}", response_model=ReputationScore)
async def get_reputation(
    agent_id: str = Path(..., description="Agent ID"),
    category: Optional[str] = Query(None, description="Reputation category"),
    system: ReputationSystem = Depends(get_reputation_system),
    current_agent: Dict[str, Any] = Depends(JWTAuth.requires_auth)
):
    """
    Get an agent's reputation score.
    
    This endpoint retrieves an agent's reputation score in the ChaosCore platform.
    """
    try:
        # Get the reputation score
        score = system.get_reputation(agent_id=agent_id, category=category)
        
        # Get the timestamp
        timestamp = system.get_last_update(agent_id=agent_id, category=category)
        
        # Return the score
        return ReputationScore(
            agent_id=agent_id,
            score=score,
            category=category,
            updated_at=timestamp or "unknown"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get reputation: {str(e)}")


@router.get("/agents/{agent_id}/history", response_model=ReputationHistoryList)
async def get_reputation_history(
    agent_id: str = Path(..., description="Agent ID"),
    category: Optional[str] = Query(None, description="Reputation category"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Page size"),
    system: ReputationSystem = Depends(get_reputation_system),
    current_agent: Dict[str, Any] = Depends(JWTAuth.requires_auth)
):
    """
    Get an agent's reputation history.
    
    This endpoint retrieves an agent's reputation history in the ChaosCore platform.
    """
    try:
        # Calculate offset
        offset = (page - 1) * page_size
        
        # Get the reputation history
        history = system.get_history(
            agent_id=agent_id,
            category=category,
            limit=page_size,
            offset=offset
        )
        
        # Convert to response model
        history_entries = []
        for entry in history:
            history_entries.append(ReputationHistory(
                agent_id=agent_id,
                score=entry.get("score", 0.0),
                category=entry.get("category"),
                timestamp=entry.get("timestamp", "unknown"),
                reason=entry.get("reason"),
                action_id=entry.get("action_id")
            ))
        
        # Return the history
        return ReputationHistoryList(
            history=history_entries,
            total=len(history_entries),  # This is not accurate, but we don't have a count method
            page=page,
            page_size=page_size
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get reputation history: {str(e)}")


@router.post("/agents/{agent_id}", response_model=ReputationScore)
async def update_reputation(
    update: ReputationUpdate,
    agent_id: str = Path(..., description="Agent ID"),
    system: ReputationSystem = Depends(get_reputation_system),
    current_agent: Dict[str, Any] = Depends(JWTAuth.requires_auth)
):
    """
    Update an agent's reputation score.
    
    This endpoint updates an agent's reputation score in the ChaosCore platform.
    """
    try:
        # Check if the current agent has permission to update reputation
        # In a real implementation, we would check if the agent has a special role
        # For now, we'll allow any agent to update reputation
        
        # Update the reputation score
        success = system.update_reputation(
            agent_id=agent_id,
            score_delta=update.score_delta,
            category=update.category,
            reason=update.reason,
            action_id=update.action_id
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update reputation score")
        
        # Get the updated score
        score = system.get_reputation(agent_id=agent_id, category=update.category)
        
        # Get the timestamp
        timestamp = system.get_last_update(agent_id=agent_id, category=update.category)
        
        # Return the updated score
        return ReputationScore(
            agent_id=agent_id,
            score=score,
            category=update.category,
            updated_at=timestamp or "unknown"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update reputation: {str(e)}")


@router.get("/top", response_model=List[ReputationScore])
async def get_top_agents(
    category: Optional[str] = Query(None, description="Reputation category"),
    limit: int = Query(10, ge=1, le=100, description="Number of top agents to retrieve"),
    system: ReputationSystem = Depends(get_reputation_system),
    current_agent: Dict[str, Any] = Depends(JWTAuth.requires_auth)
):
    """
    Get top agents by reputation score.
    
    This endpoint retrieves the top agents by reputation score in the ChaosCore platform.
    """
    try:
        # Get the top agents
        top_agents = system.get_top_agents(category=category, limit=limit)
        
        # Convert to response model
        agent_scores = []
        for agent in top_agents:
            agent_scores.append(ReputationScore(
                agent_id=agent.get("agent_id"),
                score=agent.get("score", 0.0),
                category=category,
                updated_at=agent.get("updated_at", "unknown")
            ))
        
        # Return the top agents
        return agent_scores
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get top agents: {str(e)}") 