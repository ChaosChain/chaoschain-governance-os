"""
ChaosCore SDK Exceptions

This module provides exceptions for the ChaosCore SDK.
"""

class ChaosCoreError(Exception):
    """Base exception for all ChaosCore SDK errors."""
    pass

class ChaosCoreConnectionError(ChaosCoreError):
    """Raised when a connection error occurs."""
    pass

class ChaosCoreAPIError(ChaosCoreError):
    """Raised when the API returns an error."""
    pass

class ChaosCoreAuthError(ChaosCoreError):
    """Raised when authentication fails."""
    pass

class ChaosCoreNotFoundError(ChaosCoreError):
    """Raised when a resource is not found."""
    pass 