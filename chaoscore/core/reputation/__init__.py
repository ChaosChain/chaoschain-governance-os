"""
Reputation System for ChaosCore

This module provides the core functionality for the Reputation System,
which computes, tracks, and queries reputation scores for agents in
the ChaosCore platform.
"""

from .interfaces import (
    ReputationScore,
    ReputationQueryInterface,
    ReputationComputeInterface
)

from .implementation import (
    SqlReputationSystem,
    InMemoryReputationSystem
)

__all__ = [
    # Interfaces
    'ReputationScore',
    'ReputationQueryInterface',
    'ReputationComputeInterface',
    
    # Implementations
    'SqlReputationSystem',
    'InMemoryReputationSystem'
] 