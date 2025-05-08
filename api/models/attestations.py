"""
Attestation models and CRUD operations.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import Session, relationship

from api.models.database import Base


class Attestation(Base):
    """Attestation model for database."""
    __tablename__ = "attestations"

    id = Column(Integer, primary_key=True, index=True)
    proposal_id = Column(Integer, ForeignKey("proposals.id"), unique=True)
    enclave_id = Column(String(255), nullable=False)
    payload_hash = Column(String(255), nullable=False)
    signature = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    verified_at = Column(DateTime, nullable=True)
    
    # Relationships
    proposal = relationship("Proposal", back_populates="attestation")


# CRUD operations

def create_attestation(
    db: Session, 
    proposal_id: int, 
    enclave_id: str, 
    payload_hash: str, 
    signature: str
) -> Attestation:
    """
    Create a new attestation.
    
    Args:
        db: Database session
        proposal_id: ID of the proposal
        enclave_id: ID of the enclave that generated the attestation
        payload_hash: Hash of the payload
        signature: Signature from the TEE
        
    Returns:
        Created attestation
    """
    db_attestation = Attestation(
        proposal_id=proposal_id,
        enclave_id=enclave_id,
        payload_hash=payload_hash,
        signature=signature
    )
    db.add(db_attestation)
    db.commit()
    db.refresh(db_attestation)
    return db_attestation


def get_attestation(db: Session, attestation_id: int) -> Optional[Attestation]:
    """
    Get an attestation by ID.
    
    Args:
        db: Database session
        attestation_id: ID of the attestation
        
    Returns:
        Attestation if found, None otherwise
    """
    return db.query(Attestation).filter(Attestation.id == attestation_id).first()


def get_attestation_by_proposal(db: Session, proposal_id: int) -> Optional[Attestation]:
    """
    Get an attestation for a proposal.
    
    Args:
        db: Database session
        proposal_id: ID of the proposal
        
    Returns:
        Attestation if found, None otherwise
    """
    return db.query(Attestation).filter(Attestation.proposal_id == proposal_id).first()


def mark_attestation_verified(db: Session, attestation_id: int) -> Optional[Attestation]:
    """
    Mark an attestation as verified.
    
    Args:
        db: Database session
        attestation_id: ID of the attestation
        
    Returns:
        Updated attestation if found, None otherwise
    """
    attestation = get_attestation(db, attestation_id)
    if attestation:
        attestation.verified_at = datetime.utcnow()
        db.commit()
        db.refresh(attestation)
    return attestation 