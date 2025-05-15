"""
Agent Registry Adapter Implementation

This module implements the adapter for connecting governance agents to the ChaosCore Agent Registry.
"""
import uuid
from typing import Dict, Any, Optional

from chaoscore.core.agent_registry import AgentRegistryInterface, AgentIdentity, AgentMetadata


class AgentRegistryAdapter:
    """
    Adapter for the ChaosCore Agent Registry.
    
    This adapter provides methods for registering and retrieving agents using the
    ChaosCore Agent Registry interface.
    """
    
    def __init__(self, agent_registry: AgentRegistryInterface):
        """
        Initialize the agent registry adapter.
        
        Args:
            agent_registry: ChaosCore Agent Registry implementation
        """
        self._agent_registry = agent_registry
        self._agent_cache = {}  # Cache of agent IDs to prevent duplicate registrations
    
    def register_agent(
        self,
        email: str,
        name: str,
        metadata: Dict[str, Any]
    ) -> str:
        """
        Register an agent in the ChaosCore Agent Registry.
        
        Args:
            email: Agent's email
            name: Agent's name
            metadata: Agent's metadata (capabilities, role, etc.)
            
        Returns:
            str: Agent ID
        """
        # Check if agent is already registered
        cache_key = f"{email}:{name}"
        if cache_key in self._agent_cache:
            return self._agent_cache[cache_key]
        
        # Register the agent
        agent_id = self._agent_registry.register_agent(
            email=email,
            name=name,
            metadata=metadata
        )
        
        # Cache the agent ID
        self._agent_cache[cache_key] = agent_id
        
        return agent_id
    
    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Get an agent from the ChaosCore Agent Registry.
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Dict[str, Any]: Agent data, or None if not found
        """
        agent = self._agent_registry.get_agent(agent_id)
        if agent:
            return {
                "id": agent.get_id(),
                "email": agent.get_email(),
                "name": agent.get_name(),
                "metadata": agent.get_metadata(),
                "created_at": agent.get_created_at()
            }
        return None
    
    def list_agents(self) -> list:
        """
        List all agents in the ChaosCore Agent Registry.
        
        Returns:
            list: List of agent IDs
        """
        return self._agent_registry.list_agents()
    
    def register_governance_agents(self, agent_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Register governance agents (researcher and developer).
        
        Args:
            agent_data: Dictionary with researcher and developer agent data
            
        Returns:
            Dict[str, str]: Dictionary mapping agent roles to agent IDs
        """
        agent_ids = {}
        
        # Register researcher agent
        if "researcher" in agent_data:
            researcher = agent_data["researcher"]
            researcher_id = self.register_agent(
                email=researcher.get("email", f"researcher-{uuid.uuid4()}@chaoscore.io"),
                name=researcher.get("name", "Gas Metrics Researcher"),
                metadata={
                    "role": "researcher",
                    "capabilities": ["data_analysis", "gas_metrics_analysis"],
                    "description": "Analyzes gas metrics to identify optimization opportunities"
                }
            )
            agent_ids["researcher"] = researcher_id
        
        # Register developer agent
        if "developer" in agent_data:
            developer = agent_data["developer"]
            developer_id = self.register_agent(
                email=developer.get("email", f"developer-{uuid.uuid4()}@chaoscore.io"),
                name=developer.get("name", "Parameter Optimizer"),
                metadata={
                    "role": "developer",
                    "capabilities": ["parameter_optimization", "simulation"],
                    "description": "Optimizes blockchain parameters based on research findings"
                }
            )
            agent_ids["developer"] = developer_id
        
        return agent_ids 