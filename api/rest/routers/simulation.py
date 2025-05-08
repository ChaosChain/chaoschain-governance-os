"""
API router for simulation endpoints.
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session

from api.db.session import get_db
from api.rest.dependencies import validate_api_key
from api.models.schemas import SimulationResponse, SimulationCreate, SimulationListResponse
from api.models.proposals import Proposal, ProposalStatus, get_proposal, update_proposal_status
from api.models.simulation import SimulationRun, SimulationStatus
from api.models.crud import (
    create_simulation_run,
    get_simulation_run,
    get_simulation_runs_for_proposal,
    update_simulation_status,
    update_simulation_result
)
from simulation import create_simulation

router = APIRouter(
    prefix="/simulation",
    tags=["simulation"]
)


@router.post("/{proposal_id}", response_model=SimulationResponse)
async def simulate_proposal(
    proposal_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    _: str = Depends(validate_api_key)
) -> Dict[str, Any]:
    """
    Start a simulation for a proposal.
    
    Args:
        proposal_id: ID of the proposal to simulate
        background_tasks: Background tasks
        db: Database session
        _: API key (validated by dependency)
        
    Returns:
        Created simulation run
    """
    # Check if proposal exists
    proposal = get_proposal(db, proposal_id)
    if proposal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Proposal with ID {proposal_id} not found"
        )
    
    # Create simulation run
    simulation_run = create_simulation_run(db, proposal_id)
    
    # Run simulation in background
    background_tasks.add_task(
        _run_simulation_task,
        db=db,
        simulation_id=simulation_run.id,
        proposal_id=proposal_id
    )
    
    return simulation_run


@router.get("/{simulation_id}", response_model=SimulationResponse)
def get_simulation_by_id(
    simulation_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(validate_api_key)
) -> Dict[str, Any]:
    """
    Get a simulation run by ID.
    
    Args:
        simulation_id: ID of the simulation run
        db: Database session
        _: API key (validated by dependency)
        
    Returns:
        Simulation run if found
    """
    simulation = get_simulation_run(db, simulation_id)
    if simulation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Simulation run with ID {simulation_id} not found"
        )
    return simulation


@router.get("/proposal/{proposal_id}", response_model=SimulationListResponse)
def get_simulations_for_proposal(
    proposal_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(validate_api_key)
) -> Dict[str, Any]:
    """
    Get all simulation runs for a proposal.
    
    Args:
        proposal_id: ID of the proposal
        db: Database session
        _: API key (validated by dependency)
        
    Returns:
        List of simulation runs
    """
    # Check if proposal exists
    proposal = get_proposal(db, proposal_id)
    if proposal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Proposal with ID {proposal_id} not found"
        )
    
    # Get simulation runs
    simulations = get_simulation_runs_for_proposal(db, proposal_id)
    return {"items": simulations, "total": len(simulations)}


def _run_simulation_task(db: Session, simulation_id: int, proposal_id: int) -> None:
    """
    Run simulation in background.
    
    Args:
        db: Database session
        simulation_id: ID of the simulation run
        proposal_id: ID of the proposal
    """
    try:
        # Update simulation status to running
        update_simulation_status(db, simulation_id, SimulationStatus.RUNNING)
        
        # Get proposal data
        proposal = get_proposal(db, proposal_id)
        if not proposal:
            update_simulation_status(db, simulation_id, SimulationStatus.FAILED)
            return
        
        # Run simulation
        proposal_data = {
            "proposal_id": proposal_id,
            **proposal.parameters
        }
        
        # Get simulation configuration based on simulation parameters or defaults
        transaction_count = 100
        gas_limit = 12500000
        base_fee_per_gas = 10 * 10**9
        fee_denominator = 5
        
        simulation_results = create_simulation(
            proposal_data=proposal_data,
            transaction_count=transaction_count,
            gas_limit=gas_limit,
            base_fee_per_gas=base_fee_per_gas,
            fee_denominator=fee_denominator
        )
        
        # Update simulation results
        update_simulation_result(db, simulation_id, simulation_results)
        
        # Update proposal status if needed
        if proposal.status == ProposalStatus.PENDING:
            update_proposal_status(db, proposal_id, ProposalStatus.SIMULATED)
            
    except Exception as e:
        # Update simulation status to failed
        update_simulation_status(db, simulation_id, SimulationStatus.FAILED)
        # In a real implementation, we would log the error 