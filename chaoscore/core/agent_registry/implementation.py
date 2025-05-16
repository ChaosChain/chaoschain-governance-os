"""
Agent Registry Implementation

This module provides concrete implementations of the agent registry interfaces.
"""
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any

from .interfaces import (
    AgentIdentity,
    AgentMetadata,
    AgentRegistryInterface,
    AgentNotFoundError,
    DuplicateAgentError
)


class Agent(AgentIdentity, AgentMetadata):
    """
    Implementation of an agent that combines identity and metadata.
    """
    
    def __init__(
        self,
        agent_id: str,
        public_key: str,
        name: str,
        description: str,
        capabilities: List[str],
        domains: List[str],
        created_at: datetime,
        updated_at: datetime,
        custom_metadata: Dict[str, Any],
        active: bool = True
    ):
        """
        Initialize a new agent.
        
        Args:
            agent_id: The agent's unique identifier
            public_key: The agent's public key
            name: The agent's name
            description: The agent's description
            capabilities: The agent's capabilities
            domains: The domains the agent supports
            created_at: The agent's creation timestamp
            updated_at: The agent's last update timestamp
            custom_metadata: The agent's custom metadata
            active: Whether the agent is active
        """
        self._agent_id = agent_id
        self._public_key = public_key
        self._name = name
        self._description = description
        self._capabilities = capabilities
        self._domains = domains
        self._created_at = created_at
        self._updated_at = updated_at
        self._custom_metadata = custom_metadata
        self._active = active
    
    def get_id(self) -> str:
        """
        Get the agent's unique identifier.
        
        Returns:
            str: The agent ID
        """
        return self._agent_id
    
    def get_public_key(self) -> str:
        """
        Get the agent's public key.
        
        Returns:
            str: The public key
        """
        return self._public_key
    
    def verify_signature(self, message: bytes, signature: bytes) -> bool:
        """
        Verify a signature using the agent's public key.
        
        In this implementation, we always return True for simplicity.
        In a real implementation, this would use cryptographic verification.
        
        Args:
            message: The message that was signed
            signature: The signature to verify
            
        Returns:
            bool: True if the signature is valid, False otherwise
        """
        # This is a mock implementation that always returns True
        # In a real implementation, we would use cryptographic verification
        return True
    
    def get_name(self) -> str:
        """
        Get the agent's name.
        
        Returns:
            str: The agent name
        """
        return self._name
    
    def get_description(self) -> str:
        """
        Get the agent's description.
        
        Returns:
            str: The agent description
        """
        return self._description
    
    def get_capabilities(self) -> List[str]:
        """
        Get the agent's capabilities.
        
        Returns:
            List[str]: The agent capabilities
        """
        return self._capabilities
    
    def get_supported_domains(self) -> List[str]:
        """
        Get the domains that the agent supports.
        
        Returns:
            List[str]: The supported domains
        """
        return self._domains
    
    def get_created_at(self) -> datetime:
        """
        Get the agent's creation timestamp.
        
        Returns:
            datetime: The creation timestamp
        """
        return self._created_at
    
    def get_updated_at(self) -> datetime:
        """
        Get the agent's last update timestamp.
        
        Returns:
            datetime: The last update timestamp
        """
        return self._updated_at
    
    def get_custom_metadata(self) -> Dict[str, Any]:
        """
        Get the agent's custom metadata.
        
        Returns:
            Dict[str, Any]: The custom metadata
        """
        return self._custom_metadata
    
    def is_active(self) -> bool:
        """
        Check if the agent is active.
        
        Returns:
            bool: True if the agent is active, False otherwise
        """
        return self._active
    
    def set_active(self, active: bool) -> None:
        """
        Set the agent's active status.
        
        Args:
            active: The new active status
        """
        self._active = active
    
    def update_metadata(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        capabilities: Optional[List[str]] = None,
        domains: Optional[List[str]] = None,
        custom_metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Update the agent's metadata.
        
        Args:
            name: The new name, or None to keep the current value
            description: The new description, or None to keep the current value
            capabilities: The new capabilities, or None to keep the current value
            domains: The new domains, or None to keep the current value
            custom_metadata: The new custom metadata, or None to keep the current value
        """
        if name is not None:
            self._name = name
        
        if description is not None:
            self._description = description
        
        if capabilities is not None:
            self._capabilities = capabilities
        
        if domains is not None:
            self._domains = domains
        
        if custom_metadata is not None:
            self._custom_metadata = custom_metadata
        
        self._updated_at = datetime.now()


class InMemoryAgentRegistry(AgentRegistryInterface):
    """
    In-memory implementation of the agent registry.
    
    This implementation stores agents in memory and performs all operations locally.
    It is useful for testing and development.
    """
    
    def __init__(self):
        """
        Initialize a new in-memory agent registry.
        """
        self._agents: Dict[str, Agent] = {}
        self._public_key_to_id: Dict[str, str] = {}
    
    def register_agent(self, public_key: str, metadata: Dict[str, Any], signature: str) -> str:
        """
        Register a new agent in the registry.
        
        Args:
            public_key: The agent's public key
            metadata: The agent's metadata
            signature: The signature of the metadata, signed with the agent's private key
            
        Returns:
            str: The ID of the registered agent
            
        Raises:
            DuplicateAgentError: If an agent with the same public key is already registered
        """
        # Check if an agent with this public key is already registered
        if public_key in self._public_key_to_id:
            raise DuplicateAgentError(f"Agent with public key {public_key} is already registered")
        
        # Generate a unique ID for the agent
        agent_id = str(uuid.uuid4())
        
        # Create the agent
        now = datetime.now()
        agent = Agent(
            agent_id=agent_id,
            public_key=public_key,
            name=metadata.get("name", ""),
            description=metadata.get("description", ""),
            capabilities=metadata.get("capabilities", []),
            domains=metadata.get("domains", []),
            created_at=now,
            updated_at=now,
            custom_metadata=metadata.get("custom_metadata", {}),
            active=True
        )
        
        # Store the agent
        self._agents[agent_id] = agent
        self._public_key_to_id[public_key] = agent_id
        
        return agent_id
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """
        Get an agent by ID.
        
        Args:
            agent_id: The agent ID
            
        Returns:
            Optional[Agent]: The agent, or None if not found
        """
        return self._agents.get(agent_id)
    
    def get_agent_metadata(self, agent_id: str) -> Optional[AgentMetadata]:
        """
        Get an agent's metadata by ID.
        
        Args:
            agent_id: The agent ID
            
        Returns:
            Optional[AgentMetadata]: The agent metadata, or None if not found
        """
        return self._agents.get(agent_id)
    
    def update_metadata(self, agent_id: str, metadata: Dict[str, Any], signature: str) -> None:
        """
        Update an agent's metadata.
        
        Args:
            agent_id: The agent ID
            metadata: The new metadata
            signature: The signature of the metadata, signed with the agent's private key
            
        Raises:
            AgentNotFoundError: If the agent is not found
        """
        # Get the agent
        agent = self._agents.get(agent_id)
        if agent is None:
            raise AgentNotFoundError(f"Agent with ID {agent_id} not found")
        
        # Update the agent's metadata
        agent.update_metadata(
            name=metadata.get("name"),
            description=metadata.get("description"),
            capabilities=metadata.get("capabilities"),
            domains=metadata.get("domains"),
            custom_metadata=metadata.get("custom_metadata")
        )
    
    def deactivate_agent(self, agent_id: str, signature: str) -> None:
        """
        Deactivate an agent.
        
        Args:
            agent_id: The agent ID
            signature: The signature, signed with the agent's private key
            
        Raises:
            AgentNotFoundError: If the agent is not found
        """
        # Get the agent
        agent = self._agents.get(agent_id)
        if agent is None:
            raise AgentNotFoundError(f"Agent with ID {agent_id} not found")
        
        # Deactivate the agent
        agent.set_active(False)
    
    def verify_agent(self, agent_id: str) -> bool:
        """
        Verify if an agent exists and is active.
        
        Args:
            agent_id: The agent ID
            
        Returns:
            bool: True if the agent exists and is active, False otherwise
        """
        agent = self._agents.get(agent_id)
        return agent is not None and agent.is_active()
    
    def list_agents(self, domain: Optional[str] = None, capability: Optional[str] = None) -> List[str]:
        """
        List agents, optionally filtered by domain or capability.
        
        Args:
            domain: Filter by domain
            capability: Filter by capability
            
        Returns:
            List[str]: The IDs of matching agents
        """
        result = []
        
        for agent_id, agent in self._agents.items():
            # Skip inactive agents
            if not agent.is_active():
                continue
            
            # Apply domain filter if provided
            if domain is not None and domain not in agent.get_supported_domains():
                continue
            
            # Apply capability filter if provided
            if capability is not None and capability not in agent.get_capabilities():
                continue
            
            # Agent passed all filters
            result.append(agent_id)
        
        return result 