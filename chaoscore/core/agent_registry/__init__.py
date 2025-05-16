"""
Agent Registry Module

This module provides functionality for registering and managing agent identities:
- Agent identity management
- Agent metadata storage and retrieval
- Agent verification
"""

from .interfaces import (
    AgentIdentity,
    AgentMetadata,
    AgentRegistryInterface,
    AgentNotFoundError,
    DuplicateAgentError
)
from .implementation import (
    Agent,
    InMemoryAgentRegistry
)

__all__ = [
    'AgentIdentity',
    'AgentMetadata',
    'AgentRegistryInterface',
    'AgentNotFoundError',
    'DuplicateAgentError',
    'Agent',
    'InMemoryAgentRegistry'
] 