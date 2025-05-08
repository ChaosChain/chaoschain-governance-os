"""
CRUD operations for database models.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy.orm import Session

from api.models.attestation import Attestation
from api.models.proposals import Proposal, ProposalStatus
from api.models.simulation import SimulationRun, SimulationStatus


# Attestation CRUD operations

def create_attestation(
    db: Session,
    proposal_id: int,
    enclave_id: str,
    payload_hash: str,
    signature: str,
    timestamp: int
) -> Attestation:
    """
    Create a new attestation.
    
    Args:
        db: Database session
        proposal_id: ID of the proposal
        enclave_id: ID of the enclave
        payload_hash: Hash of the payload
        signature: Signature from the TEE
        timestamp: Timestamp of the attestation
        
    Returns:
        Created attestation
    """
    db_attestation = Attestation(
        proposal_id=proposal_id,
        enclave_id=enclave_id,
        payload_hash=payload_hash,
        signature=signature,
        timestamp=timestamp
    )
    db.add(db_attestation)
    db.commit()
    db.refresh(db_attestation)
    return db_attestation


def get_attestation_by_id(db: Session, attestation_id: int) -> Optional[Attestation]:
    """
    Get an attestation by ID.
    
    Args:
        db: Database session
        attestation_id: ID of the attestation
        
    Returns:
        Attestation if found, None otherwise
    """
    return db.query(Attestation).filter(Attestation.id == attestation_id).first()


def get_attestation_by_proposal_id(db: Session, proposal_id: int) -> Optional[Attestation]:
    """
    Get an attestation by proposal ID.
    
    Args:
        db: Database session
        proposal_id: ID of the proposal
        
    Returns:
        Attestation if found, None otherwise
    """
    return db.query(Attestation).filter(Attestation.proposal_id == proposal_id).first()


def list_attestations(db: Session, skip: int = 0, limit: int = 100) -> List[Attestation]:
    """
    List attestations with pagination.
    
    Args:
        db: Database session
        skip: Number of attestations to skip
        limit: Maximum number of attestations to return
        
    Returns:
        List of attestations
    """
    return db.query(Attestation).order_by(Attestation.created_at.desc()).offset(skip).limit(limit).all()


def count_attestations(db: Session) -> int:
    """
    Count the total number of attestations.
    
    Args:
        db: Database session
        
    Returns:
        Total number of attestations
    """
    return db.query(Attestation).count()


# Simulation CRUD operations

def create_simulation_run(db: Session, proposal_id: int, configuration: Dict[str, Any] = None) -> SimulationRun:
    """
    Create a new simulation run.
    
    Args:
        db: Database session
        proposal_id: ID of the proposal to simulate
        configuration: Optional simulation configuration
        
    Returns:
        Created simulation run
    """
    db_simulation = SimulationRun(
        proposal_id=proposal_id,
        status=SimulationStatus.PENDING,
        configuration=configuration or {}
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


def update_simulation_status(db: Session, simulation_id: int, status: SimulationStatus) -> Optional[SimulationRun]:
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
        if status == SimulationStatus.RUNNING:
            simulation.started_at = datetime.utcnow()
        elif status in (SimulationStatus.COMPLETED, SimulationStatus.FAILED):
            simulation.completed_at = datetime.utcnow()
        simulation.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(simulation)
    return simulation


def update_simulation_result(db: Session, simulation_id: int, results: Dict[str, Any]) -> Optional[SimulationRun]:
    """
    Update the results of a simulation run.
    
    Args:
        db: Database session
        simulation_id: ID of the simulation run
        results: Simulation results
        
    Returns:
        Updated simulation run if found, None otherwise
    """
    simulation = get_simulation_run(db, simulation_id)
    if simulation:
        simulation.results = results
        simulation.status = SimulationStatus.COMPLETED
        simulation.completed_at = datetime.utcnow()
        simulation.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(simulation)
    return simulation 