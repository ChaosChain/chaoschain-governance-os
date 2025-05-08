"""
Proposal models and CRUD operations.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List
from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLAEnum, JSON, Text
from sqlalchemy.orm import Session, relationship

from api.models.database import Base


class ProposalStatus(str, Enum):
    """Status of a proposal."""
    PENDING = "pending"
    SIMULATED = "simulated"
    VERIFIED = "verified"


class Proposal(Base):
    """Proposal model for database."""
    __tablename__ = "proposals"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(SQLAEnum(ProposalStatus), default=ProposalStatus.PENDING)
    payload = Column(JSON, nullable=False)
    agent_sig = Column(Text, nullable=True)
    
    # Relationships
    simulation_runs = relationship("SimulationRun", back_populates="proposal", cascade="all, delete-orphan")
    attestation = relationship("Attestation", back_populates="proposal", uselist=False, cascade="all, delete-orphan")


# CRUD operations

def create_proposal(db: Session, payload: Dict[str, Any], agent_sig: Optional[str] = None) -> Proposal:
    """
    Create a new proposal.
    
    Args:
        db: Database session
        payload: JSON payload of the proposal
        agent_sig: Optional signature from the agent
        
    Returns:
        Created proposal
    """
    db_proposal = Proposal(
        payload=payload,
        agent_sig=agent_sig,
        status=ProposalStatus.PENDING
    )
    db.add(db_proposal)
    db.commit()
    db.refresh(db_proposal)
    return db_proposal


def get_proposal(db: Session, proposal_id: int) -> Optional[Proposal]:
    """
    Get a proposal by ID.
    
    Args:
        db: Database session
        proposal_id: ID of the proposal
        
    Returns:
        Proposal if found, None otherwise
    """
    return db.query(Proposal).filter(Proposal.id == proposal_id).first()


def get_proposals(db: Session, skip: int = 0, limit: int = 100) -> List[Proposal]:
    """
    Get a list of proposals with pagination.
    
    Args:
        db: Database session
        skip: Number of proposals to skip
        limit: Maximum number of proposals to return
        
    Returns:
        List of proposals
    """
    return db.query(Proposal).order_by(Proposal.created_at.desc()).offset(skip).limit(limit).all()


def update_proposal_status(db: Session, proposal_id: int, status: ProposalStatus) -> Optional[Proposal]:
    """
    Update the status of a proposal.
    
    Args:
        db: Database session
        proposal_id: ID of the proposal
        status: New status
        
    Returns:
        Updated proposal if found, None otherwise
    """
    proposal = get_proposal(db, proposal_id)
    if proposal:
        proposal.status = status
        db.commit()
        db.refresh(proposal)
    return proposal 