"""
Proof of Agency Implementation

This module provides a basic implementation of the Proof of Agency interfaces.
"""
import uuid
import json
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from ..agent_registry import AgentRegistryInterface, AgentNotFoundError
from .interfaces import (
    Action,
    Outcome,
    ActionType,
    ActionStatus,
    ProofOfAgencyInterface,
    ProofOfAgencyStorageInterface,
    ActionNotFoundError,
    OutcomeNotFoundError,
    InvalidActionError,
    ProofOfAgencyError,
    InvalidStateError,
    DistributionError
)


class ActionRecord(Action):
    """
    Implementation of the Action interface.
    """
    
    def __init__(
        self,
        action_id: str,
        agent_id: str,
        action_type: ActionType,
        description: str,
        timestamp: datetime,
        data: Dict[str, Any],
        attestation: Optional[str] = None,
        status: ActionStatus = ActionStatus.PENDING
    ):
        self._id = action_id
        self._agent_id = agent_id
        self._type = action_type
        self._description = description
        self._timestamp = timestamp
        self._data = data
        self._attestation = attestation
        self._status = status
    
    def get_id(self) -> str:
        return self._id
    
    def get_agent_id(self) -> str:
        return self._agent_id
    
    def get_type(self) -> ActionType:
        return self._type
    
    def get_description(self) -> str:
        return self._description
    
    def get_timestamp(self) -> datetime:
        return self._timestamp
    
    def get_status(self) -> ActionStatus:
        return self._status
    
    def get_data(self) -> Dict[str, Any]:
        return self._data.copy()
    
    def get_attestation(self) -> Optional[str]:
        return self._attestation
    
    def set_status(self, status: ActionStatus):
        """Update the status of the action."""
        self._status = status
    
    def set_attestation(self, attestation: str):
        """Update the attestation proof for the action."""
        self._attestation = attestation


class OutcomeRecord(Outcome):
    """
    Implementation of the Outcome interface.
    """
    
    def __init__(
        self,
        action_id: str,
        success: bool,
        impact_score: float,
        results: Dict[str, Any],
        verification_proof: Optional[str] = None
    ):
        self._action_id = action_id
        self._success = success
        self._impact_score = impact_score
        self._results = results
        self._verification_proof = verification_proof
    
    def get_action_id(self) -> str:
        return self._action_id
    
    def get_success(self) -> bool:
        return self._success
    
    def get_impact_score(self) -> float:
        return self._impact_score
    
    def get_results(self) -> Dict[str, Any]:
        return self._results.copy()
    
    def get_verification_proof(self) -> Optional[str]:
        return self._verification_proof


class InMemoryProofOfAgency(ProofOfAgencyInterface):
    """
    In-memory implementation of the Proof of Agency interface.
    """
    
    def __init__(self, agent_registry: AgentRegistryInterface):
        self._agent_registry = agent_registry
        self._actions: Dict[str, ActionRecord] = {}
        self._outcomes: Dict[str, OutcomeRecord] = {}
        self._verifications: Dict[str, List[str]] = {}  # action_id -> list of verifier_ids
        self._on_chain_records: Dict[str, Dict[str, Any]] = {}  # action_id -> on-chain data
        self._reward_distributions: Dict[str, Dict[str, float]] = {}  # action_id -> agent_id -> amount
    
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
        """
        # Verify that the agent exists
        agent = self._agent_registry.get_agent(agent_id)
        if not agent:
            raise AgentNotFoundError(f"Agent with ID {agent_id} not found")
        
        # Generate a unique ID for the action
        # In a production system, this would be more deterministic and secure
        action_id = str(uuid.uuid4())
        
        # Create and store the action
        action = ActionRecord(
            action_id=action_id,
            agent_id=agent_id,
            action_type=action_type,
            description=description,
            timestamp=datetime.now(),
            data=data,
            attestation=attestation,
            status=ActionStatus.PENDING
        )
        
        self._actions[action_id] = action
        self._verifications[action_id] = []
        
        return action_id
    
    def get_action(self, action_id: str) -> Optional[Action]:
        """
        Get an action by its identifier.
        
        Args:
            action_id: The action's unique identifier
            
        Returns:
            Optional[Action]: The action, or None if not found
        """
        return self._actions.get(action_id)
    
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
        result = []
        
        for action_id, action in self._actions.items():
            # Apply agent filter if specified
            if agent_id and action.get_agent_id() != agent_id:
                continue
            
            # Apply action type filter if specified
            if action_type and action.get_type() != action_type:
                continue
            
            # Apply status filter if specified
            if status and action.get_status() != status:
                continue
            
            result.append(action_id)
        
        return result
    
    def verify_action(self, action_id: str, verifier_id: str) -> bool:
        """
        Verify an action.
        
        Args:
            action_id: The action's unique identifier
            verifier_id: The identifier of the agent verifying the action
            
        Returns:
            bool: True if the verification was successful, False otherwise
        """
        # Verify that the action exists
        action = self._actions.get(action_id)
        if not action:
            raise ActionNotFoundError(f"Action with ID {action_id} not found")
        
        # Verify that the action is in a verifiable state
        if action.get_status() not in [ActionStatus.PENDING]:
            raise InvalidStateError(f"Action with ID {action_id} is not in a verifiable state")
        
        # Verify that the verifier exists
        verifier = self._agent_registry.get_agent(verifier_id)
        if not verifier:
            raise AgentNotFoundError(f"Verifier with ID {verifier_id} not found")
        
        # Add the verifier to the list of verifiers for this action
        self._verifications[action_id].append(verifier_id)
        
        # Update the action status
        action.set_status(ActionStatus.VERIFIED)
        
        return True
    
    def anchor_action(self, action_id: str) -> str:
        """
        Anchor an action's proof on-chain.
        
        Args:
            action_id: The action's unique identifier
            
        Returns:
            str: The transaction hash of the anchoring transaction
        """
        # Verify that the action exists
        action = self._actions.get(action_id)
        if not action:
            raise ActionNotFoundError(f"Action with ID {action_id} not found")
        
        # Verify that the action is in an anchorable state
        if action.get_status() not in [ActionStatus.VERIFIED]:
            raise InvalidStateError(f"Action with ID {action_id} is not in an anchorable state")
        
        # In a real implementation, this would call an Ethereum contract
        # For now, we just generate a mock transaction hash
        tx_hash = f"0x{uuid.uuid4().hex}"
        
        # Store the on-chain record
        self._on_chain_records[action_id] = {
            "transaction_hash": tx_hash,
            "block_number": 12345678,
            "timestamp": datetime.now().isoformat(),
            "action_data_hash": hashlib.sha256(json.dumps(action.get_data(), sort_keys=True).encode()).hexdigest(),
            "verifiers": self._verifications.get(action_id, [])
        }
        
        # Update the action status
        action.set_status(ActionStatus.ANCHORED)
        
        return tx_hash
    
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
        """
        # Verify that the action exists
        action = self._actions.get(action_id)
        if not action:
            raise ActionNotFoundError(f"Action with ID {action_id} not found")
        
        # Verify that the action is in a completable state
        if action.get_status() not in [ActionStatus.VERIFIED, ActionStatus.ANCHORED]:
            raise InvalidStateError(f"Action with ID {action_id} is not in a completable state")
        
        # Create and store the outcome
        outcome = OutcomeRecord(
            action_id=action_id,
            success=success,
            impact_score=impact_score,
            results=results,
            verification_proof=verification_proof
        )
        
        self._outcomes[action_id] = outcome
        
        # Update the action status
        action.set_status(ActionStatus.COMPLETED)
        
        return action_id
    
    def get_outcome(self, action_id: str) -> Optional[Outcome]:
        """
        Get the outcome of an action.
        
        Args:
            action_id: The action's unique identifier
            
        Returns:
            Optional[Outcome]: The outcome, or None if not available
        """
        return self._outcomes.get(action_id)
    
    def compute_rewards(self, action_id: str) -> Dict[str, float]:
        """
        Compute rewards for an action.
        
        Args:
            action_id: The action's unique identifier
            
        Returns:
            Dict[str, float]: Dictionary mapping agent IDs to reward amounts
        """
        # Verify that the action exists
        action = self._actions.get(action_id)
        if not action:
            raise ActionNotFoundError(f"Action with ID {action_id} not found")
        
        # Verify that the action is in a rewardable state
        if action.get_status() != ActionStatus.COMPLETED:
            raise InvalidStateError(f"Action with ID {action_id} is not in a rewardable state")
        
        # Verify that the outcome exists
        outcome = self._outcomes.get(action_id)
        if not outcome:
            raise InvalidStateError(f"No outcome recorded for action with ID {action_id}")
        
        # Simple reward computation:
        # - Primary agent gets base reward scaled by impact score
        # - Verifiers get a smaller verification reward
        rewards = {}
        
        # Reward for the primary agent
        primary_agent_id = action.get_agent_id()
        base_reward = 100.0  # Base reward amount
        impact_multiplier = outcome.get_impact_score()
        success_multiplier = 1.0 if outcome.get_success() else 0.25
        
        rewards[primary_agent_id] = base_reward * impact_multiplier * success_multiplier
        
        # Rewards for verifiers
        verifier_reward = base_reward * 0.1  # 10% of base reward
        for verifier_id in self._verifications.get(action_id, []):
            if verifier_id not in rewards:
                rewards[verifier_id] = 0
            rewards[verifier_id] += verifier_reward
        
        # Store the computed rewards
        self._reward_distributions[action_id] = rewards
        
        return rewards
    
    def distribute_rewards(self, action_id: str) -> str:
        """
        Distribute rewards for an action.
        
        Args:
            action_id: The action's unique identifier
            
        Returns:
            str: The transaction hash of the reward distribution transaction
        """
        # Compute rewards if not already computed
        if action_id not in self._reward_distributions:
            self.compute_rewards(action_id)
        
        # Verify that rewards have been computed
        rewards = self._reward_distributions.get(action_id)
        if not rewards:
            raise InvalidStateError(f"No rewards computed for action with ID {action_id}")
        
        # In a real implementation, this would call an Ethereum contract
        # For now, we just generate a mock transaction hash
        tx_hash = f"0x{uuid.uuid4().hex}"
        
        # In a real implementation, we would update the on-chain record
        # with the reward distribution information
        if action_id in self._on_chain_records:
            self._on_chain_records[action_id]["reward_distribution"] = {
                "transaction_hash": tx_hash,
                "timestamp": datetime.now().isoformat(),
                "rewards": rewards
            }
        
        return tx_hash

    # Interface adapter methods
    def record_action(
        self,
        agent_id: str,
        action_type: str,
        parameters: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Record a new action in the system (interface adapter method).
        
        Args:
            agent_id: The ID of the agent performing the action
            action_type: The type of action being performed
            parameters: The parameters of the action
            context: Optional context information
            
        Returns:
            str: The ID of the recorded action
        """
        # Convert string action_type to ActionType enum
        try:
            action_type_enum = ActionType(action_type)
        except ValueError:
            # Default to ANALYZE if the action type is not recognized
            action_type_enum = ActionType.ANALYZE
        
        description = parameters.get("description", "No description provided")
        
        # Combine parameters and context into data
        data = parameters.copy()
        if context:
            data["context"] = context
        
        # Call the existing implementation
        return self.log_action(
            agent_id=agent_id,
            action_type=action_type_enum,
            description=description,
            data=data
        )
    
    def update_action_status(self, action_id: str, status: ActionStatus) -> None:
        """
        Update the status of an action.
        
        Args:
            action_id: The ID of the action
            status: The new status
        """
        action = self._actions.get(action_id)
        if not action:
            raise ActionNotFoundError(f"Action with ID {action_id} not found")
        
        action.set_status(status)
    
    def attach_attestation(self, action_id: str, attestation_id: str) -> None:
        """
        Attach an attestation to an action.
        
        Args:
            action_id: The ID of the action
            attestation_id: The ID of the attestation
        """
        action = self._actions.get(action_id)
        if not action:
            raise ActionNotFoundError(f"Action with ID {action_id} not found")
        
        action.set_attestation(attestation_id)
    
    def get_agent_actions(
        self,
        agent_id: str,
        action_type: Optional[str] = None,
        status: Optional[ActionStatus] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Action]:
        """
        Get actions performed by an agent, with optional filtering.
        
        Args:
            agent_id: The ID of the agent
            action_type: Optional filter by action type
            status: Optional filter by action status
            start_time: Optional filter by start time
            end_time: Optional filter by end time
            limit: Optional limit on the number of results
            offset: Optional offset for pagination
            
        Returns:
            List[Action]: The matching actions
        """
        # Convert string action_type to ActionType enum if provided
        action_type_enum = None
        if action_type:
            try:
                action_type_enum = ActionType(action_type)
            except ValueError:
                # Skip filtering by action type if it's not recognized
                pass
        
        # Get action IDs matching the criteria
        action_ids = self.list_actions(
            agent_id=agent_id,
            action_type=action_type_enum,
            status=status
        )
        
        # Filter by time range if specified
        actions = []
        for action_id in action_ids:
            action = self._actions[action_id]
            
            # Filter by start time
            if start_time and action.get_timestamp() < start_time:
                continue
            
            # Filter by end time
            if end_time and action.get_timestamp() > end_time:
                continue
            
            actions.append(action)
        
        # Apply pagination if specified
        if offset is not None:
            actions = actions[offset:]
        
        if limit is not None:
            actions = actions[:limit]
        
        return actions
    
    def dispute_action(self, action_id: str, reason: str) -> None:
        """
        Dispute an action.
        
        Args:
            action_id: The ID of the action
            reason: The reason for the dispute
        """
        action = self._actions.get(action_id)
        if not action:
            raise ActionNotFoundError(f"Action with ID {action_id} not found")
        
        # Update the action status to disputed
        action.set_status(ActionStatus.DISPUTED)
        
        # In a real implementation, we would store the dispute reason
        # and possibly notify relevant parties 