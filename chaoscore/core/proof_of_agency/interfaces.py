"""
Proof of Agency Interfaces

This module defines the core interfaces for tracking, validating, and rewarding
agent actions in the ChaosCore platform.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum


class ActionStatus(Enum):
    """
    Status of an action in the Proof of Agency system.
    """
    PENDING = "pending"          # Action is logged but not yet verified
    VERIFIED = "verified"        # Action has been verified
    ANCHORED = "anchored"        # Action has been anchored on-chain
    COMPLETED = "completed"      # Action has been completed and assessed
    REJECTED = "rejected"        # Action was rejected during verification
    REVOKED = "revoked"          # Action was revoked after verification


class ActionType(Enum):
    """
    Types of actions that can be performed by agents.
    """
    ANALYZE = "analyze"          # Analyze data or information
    PROPOSE = "propose"          # Propose a solution or change
    VERIFY = "verify"            # Verify information or results
    EXECUTE = "execute"          # Execute an operation
    MONITOR = "monitor"          # Monitor a system or process
    COLLABORATE = "collaborate"  # Collaborate with other agents


class Action(ABC):
    """
    Interface for agent actions.
    """
    
    @abstractmethod
    def get_id(self) -> str:
        """
        Get the unique identifier of the action.
        
        Returns:
            str: The action's unique identifier
        """
        pass
    
    @abstractmethod
    def get_agent_id(self) -> str:
        """
        Get the identifier of the agent that performed the action.
        
        Returns:
            str: The agent's unique identifier
        """
        pass
    
    @abstractmethod
    def get_type(self) -> ActionType:
        """
        Get the type of the action.
        
        Returns:
            ActionType: The action type
        """
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """
        Get the description of the action.
        
        Returns:
            str: The action's description
        """
        pass
    
    @abstractmethod
    def get_timestamp(self) -> datetime:
        """
        Get the timestamp when the action was performed.
        
        Returns:
            datetime: The action timestamp
        """
        pass
    
    @abstractmethod
    def get_status(self) -> ActionStatus:
        """
        Get the current status of the action.
        
        Returns:
            ActionStatus: The action status
        """
        pass
    
    @abstractmethod
    def get_data(self) -> Dict[str, Any]:
        """
        Get the data associated with the action.
        
        Returns:
            Dict[str, Any]: The action data
        """
        pass
    
    @abstractmethod
    def get_attestation(self) -> Optional[str]:
        """
        Get the attestation proof for the action.
        
        Returns:
            Optional[str]: The attestation proof, or None if not available
        """
        pass


class Outcome(ABC):
    """
    Interface for action outcomes.
    """
    
    @abstractmethod
    def get_action_id(self) -> str:
        """
        Get the identifier of the associated action.
        
        Returns:
            str: The action's unique identifier
        """
        pass
    
    @abstractmethod
    def get_success(self) -> bool:
        """
        Get whether the action was successful.
        
        Returns:
            bool: True if the action was successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_impact_score(self) -> float:
        """
        Get the impact score of the action.
        
        Returns:
            float: The impact score, typically between 0 and 1
        """
        pass
    
    @abstractmethod
    def get_results(self) -> Dict[str, Any]:
        """
        Get the results of the action.
        
        Returns:
            Dict[str, Any]: The action results
        """
        pass
    
    @abstractmethod
    def get_verification_proof(self) -> Optional[str]:
        """
        Get the verification proof for the outcome.
        
        Returns:
            Optional[str]: The verification proof, or None if not available
        """
        pass


class ProofOfAgencyInterface(ABC):
    """
    Interface for Proof of Agency operations.
    """
    
    @abstractmethod
    def log_action(self, agent_id: str, action_type: ActionType, description: str, 
                  data: Dict[str, Any], attestation: Optional[str] = None) -> str:
        """
        Log an action performed by an agent.
        
        Args:
            agent_id: The agent's unique identifier
            action_type: The type of the action
            description: A description of the action
            data: The data associated with the action
            attestation: Optional attestation proof
            
        Returns:
            str: The unique identifier assigned to the action
            
        Raises:
            ValueError: If the action data is invalid
            AgentNotFoundError: If the agent is not found
        """
        pass
    
    @abstractmethod
    def get_action(self, action_id: str) -> Optional[Action]:
        """
        Get an action by its identifier.
        
        Args:
            action_id: The action's unique identifier
            
        Returns:
            Optional[Action]: The action, or None if not found
        """
        pass
    
    @abstractmethod
    def list_actions(self, agent_id: Optional[str] = None, 
                    action_type: Optional[ActionType] = None,
                    status: Optional[ActionStatus] = None) -> List[str]:
        """
        List actions matching the specified criteria.
        
        Args:
            agent_id: Optional agent filter
            action_type: Optional action type filter
            status: Optional status filter
            
        Returns:
            List[str]: List of action identifiers matching the criteria
        """
        pass
    
    @abstractmethod
    def verify_action(self, action_id: str, verifier_id: str) -> bool:
        """
        Verify an action.
        
        Args:
            action_id: The action's unique identifier
            verifier_id: The identifier of the agent verifying the action
            
        Returns:
            bool: True if the verification was successful, False otherwise
            
        Raises:
            ActionNotFoundError: If the action is not found
            InvalidStateError: If the action is not in a verifiable state
        """
        pass
    
    @abstractmethod
    def anchor_action(self, action_id: str) -> str:
        """
        Anchor an action's proof on-chain.
        
        Args:
            action_id: The action's unique identifier
            
        Returns:
            str: The transaction hash of the anchoring transaction
            
        Raises:
            ActionNotFoundError: If the action is not found
            InvalidStateError: If the action is not in an anchorable state
            AnchoringError: If the anchoring fails
        """
        pass
    
    @abstractmethod
    def record_outcome(self, action_id: str, success: bool, impact_score: float,
                      results: Dict[str, Any], verification_proof: Optional[str] = None) -> str:
        """
        Record the outcome of an action.
        
        Args:
            action_id: The action's unique identifier
            success: Whether the action was successful
            impact_score: The impact score of the action
            results: The results of the action
            verification_proof: Optional verification proof
            
        Returns:
            str: The unique identifier assigned to the outcome
            
        Raises:
            ActionNotFoundError: If the action is not found
            InvalidStateError: If the action is not in a completable state
        """
        pass
    
    @abstractmethod
    def get_outcome(self, action_id: str) -> Optional[Outcome]:
        """
        Get the outcome of an action.
        
        Args:
            action_id: The action's unique identifier
            
        Returns:
            Optional[Outcome]: The outcome, or None if not available
        """
        pass
    
    @abstractmethod
    def compute_rewards(self, action_id: str) -> Dict[str, float]:
        """
        Compute rewards for an action.
        
        Args:
            action_id: The action's unique identifier
            
        Returns:
            Dict[str, float]: Dictionary mapping agent IDs to reward amounts
            
        Raises:
            ActionNotFoundError: If the action is not found
            InvalidStateError: If the action is not in a rewardable state
        """
        pass
    
    @abstractmethod
    def distribute_rewards(self, action_id: str) -> str:
        """
        Distribute rewards for an action.
        
        Args:
            action_id: The action's unique identifier
            
        Returns:
            str: The transaction hash of the reward distribution transaction
            
        Raises:
            ActionNotFoundError: If the action is not found
            InvalidStateError: If the action is not in a rewardable state
            DistributionError: If the distribution fails
        """
        pass


# Custom exceptions
class ProofOfAgencyError(Exception):
    """Base exception for Proof of Agency errors."""
    pass


class ActionNotFoundError(ProofOfAgencyError):
    """Exception raised when an action is not found."""
    pass


class InvalidStateError(ProofOfAgencyError):
    """Exception raised when an action is in an invalid state for the requested operation."""
    pass


class DistributionError(ProofOfAgencyError):
    """Exception raised when reward distribution fails."""
    pass 