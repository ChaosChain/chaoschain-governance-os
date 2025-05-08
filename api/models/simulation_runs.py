"""
Simulation runs models and CRUD operations.
"""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List
from sqlalchemy import Column, Integer, DateTime, JSON, ForeignKey, Enum as SQLAEnum
from sqlalchemy.orm import Session, relationship

from api.models.database import Base


class SimulationStatus(str, Enum):
    """Status of a simulation run."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class SimulationRun(Base):
    """Simulation run model for database."""
    __tablename__ = "simulation_runs"

    id = Column(Integer, primary_key=True, index=True)
    proposal_id = Column(Integer, ForeignKey("proposals.id"))
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    status = Column(SQLAEnum(SimulationStatus), default=SimulationStatus.PENDING)
    result = Column(JSON, nullable=True)
    metrics = Column(JSON, nullable=True)
    
    # Relationships
    proposal = relationship("Proposal", back_populates="simulation_runs")


# CRUD operations

def create_simulation_run(db: Session, proposal_id: int) -> SimulationRun:
    """
    Create a new simulation run.
    
    Args:
        db: Database session
        proposal_id: ID of the proposal to simulate
        
    Returns:
        Created simulation run
    """
    db_simulation = SimulationRun(
        proposal_id=proposal_id,
        status=SimulationStatus.PENDING
    )
    db.add(db_simulation)
    db.commit()
    db.refresh(db_simulation)
    return db_simulation


def get_simulation_run(db: Session, simulation_id: int) -> Optional[SimulationRun]:
    """
    Get a simulation run by ID.
    
    Args:
        db: Database session
        simulation_id: ID of the simulation run
        
    Returns:
        SimulationRun if found, None otherwise
    """
    return db.query(SimulationRun).filter(SimulationRun.id == simulation_id).first()


def get_simulation_runs_for_proposal(db: Session, proposal_id: int) -> List[SimulationRun]:
    """
    Get all simulation runs for a proposal.
    
    Args:
        db: Database session
        proposal_id: ID of the proposal
        
    Returns:
        List of simulation runs
    """
    return db.query(SimulationRun).filter(SimulationRun.proposal_id == proposal_id).all()


def update_simulation_result(
    db: Session, 
    simulation_id: int, 
    result: Dict[str, Any], 
    metrics: Dict[str, Any]
) -> Optional[SimulationRun]:
    """
    Update the results and metrics of a simulation run.
    
    Args:
        db: Database session
        simulation_id: ID of the simulation run
        result: Simulation result
        metrics: Simulation metrics
        
    Returns:
        Updated simulation run if found, None otherwise
    """
    simulation = get_simulation_run(db, simulation_id)
    if simulation:
        simulation.result = result
        simulation.metrics = metrics
        simulation.status = SimulationStatus.COMPLETED
        simulation.completed_at = datetime.utcnow()
        db.commit()
        db.refresh(simulation)
    return simulation


def update_simulation_status(
    db: Session, 
    simulation_id: int, 
    status: SimulationStatus
) -> Optional[SimulationRun]:
    """
    Update the status of a simulation run.
    
    Args:
        db: Database session
        simulation_id: ID of the simulation run
        status: New status
        
    Returns:
        Updated simulation run if found, None otherwise
    """
    simulation = get_simulation_run(db, simulation_id)
    if simulation:
        simulation.status = status
        if status == SimulationStatus.COMPLETED or status == SimulationStatus.FAILED:
            simulation.completed_at = datetime.utcnow()
        db.commit()
        db.refresh(simulation)
    return simulation 