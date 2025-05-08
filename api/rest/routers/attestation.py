"""
API router for TEE attestation endpoints.
"""

from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from api.rest.dependencies import get_db, validate_api_key
from api.models.schemas import AttestationCreate, AttestationResponse
from api.models.crud import (
    create_attestation,
    get_attestation_by_id,
    get_attestation_by_proposal_id,
    list_attestations
)
from verification.tee import phala_stub

router = APIRouter(
    prefix="/attestation",
    tags=["attestation"],
)


@router.post("/generate", response_model=AttestationResponse)
def generate_attestation(
    attestation_data: AttestationCreate,
    db: Session = Depends(get_db),
    _: str = Depends(validate_api_key)
) -> Dict[str, Any]:
    """
    Generate a new TEE attestation.
    
    Args:
        attestation_data: Data to attest
        db: Database session
        _: API key (validated by dependency)
        
    Returns:
        Attestation data
    """
    # Generate attestation using Phala stub
    attestation_payload = {
        "proposal_id": attestation_data.proposal_id,
        "data": attestation_data.data
    }
    
    attestation_result = phala_stub.generate_attestation(attestation_payload)
    
    # Store attestation in database
    db_attestation = create_attestation(
        db=db,
        proposal_id=attestation_data.proposal_id,
        enclave_id=attestation_result["enclave_id"],
        payload_hash=attestation_result["payload_hash"],
        signature=attestation_result["signature"],
        timestamp=attestation_result["timestamp"]
    )
    
    return db_attestation


@router.get("/{attestation_id}", response_model=AttestationResponse)
def get_attestation(
    attestation_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(validate_api_key)
) -> Dict[str, Any]:
    """
    Get attestation by ID.
    
    Args:
        attestation_id: Attestation ID
        db: Database session
        _: API key (validated by dependency)
        
    Returns:
        Attestation data
    """
    attestation = get_attestation_by_id(db, attestation_id)
    if not attestation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Attestation with ID {attestation_id} not found"
        )
    return attestation


@router.get("/proposal/{proposal_id}", response_model=AttestationResponse)
def get_attestation_for_proposal(
    proposal_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(validate_api_key)
) -> Dict[str, Any]:
    """
    Get attestation by proposal ID.
    
    Args:
        proposal_id: Proposal ID
        db: Database session
        _: API key (validated by dependency)
        
    Returns:
        Attestation data
    """
    attestation = get_attestation_by_proposal_id(db, proposal_id)
    if not attestation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No attestation found for proposal ID {proposal_id}"
        )
    return attestation 