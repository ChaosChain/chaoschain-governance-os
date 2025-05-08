"""
API request and response schemas.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class ProposalStatus(str, Enum):
    """Status of a proposal."""
    PENDING = "pending"
    SIMULATED = "simulated"
    VERIFIED = "verified"


class SimulationStatus(str, Enum):
    """Status of a simulation run."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


# Request models
class ProposalCreate(BaseModel):
    """Schema for creating a new proposal."""
    payload: Dict[str, Any] = Field(..., description="JSON payload of the proposal")
    agent_sig: Optional[str] = Field(None, description="Signature from the agent")


# Response models
class AttestationResponse(BaseModel):
    """Schema for attestation response."""
    id: int
    enclave_id: str
    payload_hash: str
    signature: str
    created_at: datetime
    verified_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class SimulationRunResponse(BaseModel):
    """Schema for simulation run response."""
    id: int
    proposal_id: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    status: SimulationStatus
    result: Optional[Dict[str, Any]] = None
    metrics: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


class ProposalResponse(BaseModel):
    """Schema for proposal response."""
    id: int
    created_at: datetime
    status: ProposalStatus
    payload: Dict[str, Any]
    agent_sig: Optional[str] = None
    simulation_runs: List[SimulationRunResponse] = []
    attestation: Optional[AttestationResponse] = None
    
    class Config:
        from_attributes = True


class ProposalListResponse(BaseModel):
    """Schema for proposal list response."""
    items: List[ProposalResponse]
    total: int 