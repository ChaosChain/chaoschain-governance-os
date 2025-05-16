"""
Proof of Agency Module

This module provides the core functionality for the Proof of Agency framework,
which enables recording, verifying, and querying agent actions and their outcomes.
"""

from .interfaces import (
    Action,
    Outcome,
    ActionStatus,
    ActionType,
    ProofOfAgencyInterface,
    ProofOfAgencyStorageInterface,
    ActionNotFoundError,
    OutcomeNotFoundError,
    InvalidActionError,
    ProofOfAgencyError,
    InvalidStateError,
    DistributionError
)

from .implementation import (
    ActionRecord,
    OutcomeRecord,
    InMemoryProofOfAgency
)

__all__ = [
    # Interfaces
    'Action',
    'Outcome',
    'ActionStatus',
    'ActionType',
    'ProofOfAgencyInterface',
    'ProofOfAgencyStorageInterface',
    
    # Implementations
    'ActionRecord',
    'OutcomeRecord',
    'InMemoryProofOfAgency',
    
    # Exceptions
    'ActionNotFoundError',
    'OutcomeNotFoundError',
    'InvalidActionError',
    'ProofOfAgencyError',
    'InvalidStateError',
    'DistributionError'
] 