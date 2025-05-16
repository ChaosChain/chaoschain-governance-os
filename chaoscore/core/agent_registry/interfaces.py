"""
Agent Registry Interfaces

This module defines the interfaces for agent identity and registry components.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime


class AgentIdentity(ABC):
    """
    Interface defining an agent's identity.
    """
    
    @abstractmethod
    def get_id(self) -> str:
        """
        Get the agent's unique identifier.
        
        Returns:
            str: The agent ID
        """
        pass
    
    @abstractmethod
    def get_public_key(self) -> str:
        """
        Get the agent's public key.
        
        Returns:
            str: The public key
        """
        pass
    
    @abstractmethod
    def verify_signature(self, message: bytes, signature: bytes) -> bool:
        """
        Verify a signature using the agent's public key.
        
        Args:
            message: The message that was signed
            signature: The signature to verify
            
        Returns:
            bool: True if the signature is valid, False otherwise
        """
        pass


class AgentMetadata(ABC):
    """
    Interface defining an agent's metadata.
    """
    
    @abstractmethod
    def get_name(self) -> str:
        """
        Get the agent's name.
        
        Returns:
            str: The agent name
        """
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """
        Get the agent's description.
        
        Returns:
            str: The agent description
        """
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """
        Get the agent's capabilities.
        
        Returns:
            List[str]: The agent capabilities
        """
        pass
    
    @abstractmethod
    def get_supported_domains(self) -> List[str]:
        """
        Get the domains that the agent supports.
        
        Returns:
            List[str]: The supported domains
        """
        pass
    
    @abstractmethod
    def get_created_at(self) -> datetime:
        """
        Get the agent's creation timestamp.
        
        Returns:
            datetime: The creation timestamp
        """
        pass
    
    @abstractmethod
    def get_updated_at(self) -> datetime:
        """
        Get the agent's last update timestamp.
        
        Returns:
            datetime: The last update timestamp
        """
        pass
    
    @abstractmethod
    def get_custom_metadata(self) -> Dict[str, Any]:
        """
        Get the agent's custom metadata.
        
        Returns:
            Dict[str, Any]: The custom metadata
        """
        pass


class AgentRegistryInterface(ABC):
    """
    Interface for agent registry operations.
    """
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    def get_agent(self, agent_id: str) -> Optional[AgentIdentity]:
        """
        Get an agent by ID.
        
        Args:
            agent_id: The agent ID
            
        Returns:
            Optional[AgentIdentity]: The agent, or None if not found
        """
        pass
    
    @abstractmethod
    def get_agent_metadata(self, agent_id: str) -> Optional[AgentMetadata]:
        """
        Get an agent's metadata by ID.
        
        Args:
            agent_id: The agent ID
            
        Returns:
            Optional[AgentMetadata]: The agent metadata, or None if not found
        """
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    def deactivate_agent(self, agent_id: str, signature: str) -> None:
        """
        Deactivate an agent.
        
        Args:
            agent_id: The agent ID
            signature: The signature, signed with the agent's private key
            
        Raises:
            AgentNotFoundError: If the agent is not found
        """
        pass
    
    @abstractmethod
    def verify_agent(self, agent_id: str) -> bool:
        """
        Verify if an agent exists and is active.
        
        Args:
            agent_id: The agent ID
            
        Returns:
            bool: True if the agent exists and is active, False otherwise
        """
        pass
    
    @abstractmethod
    def list_agents(self, domain: Optional[str] = None, capability: Optional[str] = None) -> List[str]:
        """
        List agents, optionally filtered by domain or capability.
        
        Args:
            domain: Filter by domain
            capability: Filter by capability
            
        Returns:
            List[str]: The IDs of matching agents
        """
        pass


class AgentNotFoundError(Exception):
    """Exception raised when an agent is not found."""
    pass


class DuplicateAgentError(Exception):
    """Exception raised when trying to register an agent that already exists."""
    pass


class AgentOnChainRegistry(ABC):
    """
    Interface for on-chain agent registry operations.
    """
    
    @abstractmethod
    def anchor_identity(self, agent_id: str) -> str:
        """
        Anchor an agent's identity on-chain.
        
        Args:
            agent_id: The agent's unique identifier
            
        Returns:
            str: The transaction hash of the anchoring transaction
            
        Raises:
            AgentNotFoundError: If the agent is not found
            AnchoringError: If the anchoring fails
        """
        pass
    
    @abstractmethod
    def verify_anchoring(self, agent_id: str) -> bool:
        """
        Verify if an agent's identity is anchored on-chain.
        
        Args:
            agent_id: The agent's unique identifier
            
        Returns:
            bool: True if the agent is anchored, False otherwise
            
        Raises:
            AgentNotFoundError: If the agent is not found
        """
        pass
    
    @abstractmethod
    def get_on_chain_data(self, agent_id: str) -> Dict[str, Any]:
        """
        Get on-chain data for an agent.
        
        Args:
            agent_id: The agent's unique identifier
            
        Returns:
            Dict[str, Any]: Dictionary of on-chain data
            
        Raises:
            AgentNotFoundError: If the agent is not found
        """
        pass
    
    @abstractmethod
    def update_on_chain_data(self, agent_id: str, data: Dict[str, Any], signature: str) -> str:
        """
        Update on-chain data for an agent.
        
        Args:
            agent_id: The agent's unique identifier
            data: The data to update
            signature: Signature of the data, signed with the private key
            
        Returns:
            str: The transaction hash of the update transaction
            
        Raises:
            AgentNotFoundError: If the agent is not found
            ValueError: If the data or signature is invalid
            UpdateError: If the update fails
        """
        pass


# Custom exceptions
class AgentRegistryError(Exception):
    """Base exception for agent registry errors."""
    pass


class AnchoringError(AgentRegistryError):
    """Exception raised when anchoring an agent's identity on-chain fails."""
    pass


class UpdateError(AgentRegistryError):
    """Exception raised when updating agent data fails."""
    pass 