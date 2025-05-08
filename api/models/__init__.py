"""
Models package initializer.

Imports all models to fix circular imports and provide a central
import point.
"""

from api.models.base import Base
from api.models.proposals import Proposal, ProposalStatus
from api.models.simulation import SimulationRun, SimulationStatus
from api.models.attestation import Attestation
from api.db.session import engine, get_db

# Export models and database components
__all__ = [
    'Base', 'engine', 'get_db',
    'Proposal', 'ProposalStatus',
    'SimulationRun', 'SimulationStatus',
    'Attestation'
]

# Create all tables in the engine
# This is equivalent to "Create Table" statements in raw SQL
# Base.metadata.create_all(bind=engine) 