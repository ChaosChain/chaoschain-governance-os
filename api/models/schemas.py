"""
API schema models using Pydantic.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field


# Base Schemas

class ProposalBase(BaseModel):
    """Base schema for proposal data."""
    title: str
    description: str
    chain_id: int
    parameters: Dict[str, Any]  # JSON data for proposal parameters


class SimulationBase(BaseModel):
    """Base schema for simulation data."""
    proposal_id: int
    configuration: Dict[str, Any] = Field(default_factory=dict)  # Simulation config


class AttestationBase(BaseModel):
    """Base schema for attestation data."""
    proposal_id: int
    data: Dict[str, Any] = Field(default_factory=dict)  # Data to attest


# Create Schemas

class ProposalCreate(ProposalBase):
    """Schema for creating a new proposal."""
    pass


class SimulationCreate(SimulationBase):
    """Schema for creating a new simulation run."""
    pass


class AttestationCreate(AttestationBase):
    """Schema for creating a new attestation."""
    pass


# Response Schemas

class ProposalResponse(ProposalBase):
    """Schema for proposal response data."""
    id: int
    created_at: datetime
    updated_at: datetime
    status: str
    
    class Config:
        """Pydantic config."""
        from_attributes = True


class SimulationResponse(SimulationBase):
    """Schema for simulation response data."""
    id: int
    created_at: datetime
    updated_at: datetime
    status: str
    results: Optional[Dict[str, Any]] = None
    
    class Config:
        """Pydantic config."""
        from_attributes = True


class AttestationResponse(BaseModel):
    """Schema for attestation response data."""
    id: int
    proposal_id: int
    enclave_id: str
    payload_hash: str
    signature: str
    timestamp: int
    created_at: datetime
    
    class Config:
        """Pydantic config."""
        from_attributes = True


# Update Schemas

class ProposalUpdate(BaseModel):
    """Schema for updating a proposal."""
    title: Optional[str] = None
    description: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    status: Optional[str] = None


class ProposalStatusUpdate(BaseModel):
    """Schema for updating proposal status."""
    status: str


class SimulationStatusUpdate(BaseModel):
    """Schema for updating simulation status."""
    status: str
    results: Optional[Dict[str, Any]] = None


# List Response Schemas

class ProposalListResponse(BaseModel):
    """Schema for list of proposals response."""
    items: List[ProposalResponse]
    total: int


class SimulationListResponse(BaseModel):
    """Schema for list of simulations response."""
    items: List[SimulationResponse]
    total: int 