"""
Verification package.

This package provides functionality for verifying the integrity
and security of the ChaosChain Governance OS.
"""

from .tee import PhalaAttestationStub, phala_stub

__all__ = ['PhalaAttestationStub', 'phala_stub'] 