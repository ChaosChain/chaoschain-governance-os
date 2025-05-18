"""
Governance tasks for the ChaosCore platform.

This package contains task implementations for blockchain governance analysis and optimization.
"""

# Import task registry
from agent.task_registry import Task, TaskRegistry, registry, register_task

# Import task implementations
from .gas_parameter_optimizer import GasParameterOptimizer
from .proposal_sanity_scanner import ProposalSanityScanner
from .mev_cost_estimator import MEVCostEstimator

# Export classes
__all__ = [
    'Task',
    'TaskRegistry',
    'registry',
    'register_task',
    'GasParameterOptimizer',
    'ProposalSanityScanner',
    'MEVCostEstimator',
] 