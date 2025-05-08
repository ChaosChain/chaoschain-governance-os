"""
API router for proposal endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.models.database import get_db
from api.models.proposals import create_proposal, get_proposal, get_proposals, update_proposal_status, ProposalStatus
from api.auth.api_key import get_api_key
from api.rest.schemas import ProposalCreate, ProposalResponse, ProposalListResponse

router = APIRouter(prefix="/proposals", tags=["proposals"])


@router.post("", response_model=ProposalResponse, status_code=status.HTTP_201_CREATED)
async def create_new_proposal(
    proposal: ProposalCreate,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key)
):
    """
    Create a new proposal.
    
    Args:
        proposal: Proposal data
        db: Database session
        api_key: API key
        
    Returns:
        Created proposal
    """
    db_proposal = create_proposal(db, proposal.payload, proposal.agent_sig)
    return db_proposal


@router.get("/{proposal_id}", response_model=ProposalResponse)
async def get_proposal_by_id(
    proposal_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key)
):
    """
    Get a proposal by ID.
    
    Args:
        proposal_id: ID of the proposal
        db: Database session
        api_key: API key
        
    Returns:
        Proposal if found
        
    Raises:
        HTTPException: If proposal not found
    """
    db_proposal = get_proposal(db, proposal_id)
    if db_proposal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Proposal with ID {proposal_id} not found"
        )
    return db_proposal


@router.get("", response_model=ProposalListResponse)
async def list_proposals(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key)
):
    """
    List proposals with pagination.
    
    Args:
        skip: Number of proposals to skip
        limit: Maximum number of proposals to return
        db: Database session
        api_key: API key
        
    Returns:
        List of proposals
    """
    proposals = get_proposals(db, skip, limit)
    total = db.query(get_proposal.__annotations__["return"].__args__[0]).count()
    return {"items": proposals, "total": total}


@router.patch("/{proposal_id}/status", response_model=ProposalResponse)
async def update_status(
    proposal_id: int,
    status: ProposalStatus,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key)
):
    """
    Update the status of a proposal.
    
    Args:
        proposal_id: ID of the proposal
        status: New status
        db: Database session
        api_key: API key
        
    Returns:
        Updated proposal
        
    Raises:
        HTTPException: If proposal not found
    """
    db_proposal = update_proposal_status(db, proposal_id, status)
    if db_proposal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Proposal with ID {proposal_id} not found"
        )
    return db_proposal 