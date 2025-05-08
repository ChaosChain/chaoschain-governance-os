"""
Database model for simulation runs.
"""

from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, DateTime, JSON, ForeignKey, Enum as SQLAEnum
from sqlalchemy.orm import relationship

from api.models.base import Base


class SimulationStatus(str, Enum):
    """Status of a simulation run."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class SimulationRun(Base):
    """
    Database model for simulation runs.
    
    Each simulation run represents an execution of a blockchain
    simulation for a specific proposal.
    """
    
    __tablename__ = "simulation_runs"

    id = Column(Integer, primary_key=True, index=True)
    proposal_id = Column(Integer, ForeignKey("proposals.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    status = Column(SQLAEnum(SimulationStatus), default=SimulationStatus.PENDING, nullable=False)
    configuration = Column(JSON, nullable=True)
    results = Column(JSON, nullable=True)
    
    # Relationships
    proposal = relationship("Proposal", back_populates="simulation_runs")
    
    def __repr__(self) -> str:
        """
        String representation of the simulation run.
        
        Returns:
            String representation
        """
        return f"<SimulationRun(id={self.id}, proposal_id={self.proposal_id}, status={self.status})>" 