"""
Database model for attestations.
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime, func
from sqlalchemy.orm import relationship

from api.models.base import Base


class Attestation(Base):
    """
    Database model for TEE attestations.
    
    Each attestation represents a verification of a proposal
    by a trusted execution environment.
    """
    
    __tablename__ = "attestations"
    
    id = Column(Integer, primary_key=True, index=True)
    proposal_id = Column(Integer, ForeignKey("proposals.id"), nullable=False)
    enclave_id = Column(String(255), nullable=False, index=True)
    payload_hash = Column(String(255), nullable=False)
    signature = Column(Text, nullable=False)
    timestamp = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relationships
    proposal = relationship("Proposal", back_populates="attestations")
    
    def __repr__(self) -> str:
        """
        String representation of the attestation.
        
        Returns:
            String representation
        """
        return f"<Attestation(id={self.id}, proposal_id={self.proposal_id}, enclave_id={self.enclave_id})>" 