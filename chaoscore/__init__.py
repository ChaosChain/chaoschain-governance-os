"""
ChaosCore: AI Agent Governance Platform

ChaosCore is a platform for governing and coordinating autonomous AI agents.
It provides components for agent identity, registry, reputation, and blockchain integration.
"""

__version__ = "0.1.0"
__author__ = "ChaosCore Team"
__email__ = "info@chaoscore.ai"

# Import core components
from .core import agent_registry
try:
    from .core import ethereum
except ImportError:
    # Handle case where ethereum dependencies are not installed
    pass 