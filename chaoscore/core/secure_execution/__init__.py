"""
Secure Execution Module

This module provides the core functionality for the Secure Execution Environment,
which enables secure and attested execution of agent code.
"""

from .interfaces import (
    SecureExecutionEnvironment,
    AttestationProvider,
    Attestation,
    ExecutionResult,
    ExecutionStatus,
    SecureExecutionError,
    AttestationVerificationError,
    EnvironmentSetupError,
    ExecutionTimeoutError
)

from .implementation import (
    MockSecureExecutionEnvironment,
    MockAttestationProvider
)

__all__ = [
    # Interfaces
    'SecureExecutionEnvironment',
    'AttestationProvider',
    'Attestation',
    'ExecutionResult',
    'ExecutionStatus',
    
    # Implementations
    'MockSecureExecutionEnvironment',
    'MockAttestationProvider',
    
    # Exceptions
    'SecureExecutionError',
    'AttestationVerificationError',
    'EnvironmentSetupError',
    'ExecutionTimeoutError'
] 