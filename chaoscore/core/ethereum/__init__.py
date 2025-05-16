"""
Ethereum Integration Module

This module provides Ethereum blockchain integration for the ChaosCore platform.
It enables transaction signing, smart contract interaction, and event monitoring.
"""

from .interfaces import BlockchainClient, ContractInteraction, TransactionManager, EventMonitor
from .implementation import EthereumClient

__all__ = [
    'BlockchainClient',
    'ContractInteraction',
    'TransactionManager',
    'EventMonitor',
    'EthereumClient',
] 