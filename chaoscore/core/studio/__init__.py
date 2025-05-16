"""
Studio Framework for ChaosCore

This module provides the core functionality for the Studio Framework,
which enables the creation and management of collaborative agent workspaces.
"""

from .interfaces import (
    Studio,
    StudioManager,
    Task,
    TaskStatus,
    TaskResult,
    StudioException,
    TaskNotFoundException,
    InvalidTaskStateException
)

from .implementation import (
    BasicStudio,
    InMemoryStudioManager,
    BasicTask
)

__all__ = [
    # Interfaces
    'Studio',
    'StudioManager',
    'Task',
    'TaskStatus',
    'TaskResult',
    
    # Implementations
    'BasicStudio',
    'InMemoryStudioManager',
    'BasicTask',
    
    # Exceptions
    'StudioException',
    'TaskNotFoundException',
    'InvalidTaskStateException'
] 