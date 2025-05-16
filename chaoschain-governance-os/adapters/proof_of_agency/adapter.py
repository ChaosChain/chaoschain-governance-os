"""
Proof of Agency Adapter Implementation

This module implements the adapter for connecting the governance system to the ChaosCore
Proof of Agency framework.
"""
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime

from chaoscore.core.proof_of_agency import (
    ProofOfAgencyInterface,
    ActionType,
    ActionStatus,
    Action,
    Outcome
)


class ProofOfAgencyAdapter:
    """
    Adapter for the ChaosCore Proof of Agency framework.
    
    This adapter provides methods for logging and verifying actions using the
    ChaosCore Proof of Agency interface.
    """
    
    def __init__(self, proof_of_agency: ProofOfAgencyInterface):
        """
        Initialize the proof of agency adapter.
        
        Args:
            proof_of_agency: ChaosCore Proof of Agency implementation
        """
        self._poa = proof_of_agency
        self._action_cache = {}  # Cache of action IDs to prevent duplicate logging
    
    def log_action(
        self,
        agent_id: str,
        action_type: str,
        description: str,
        data: Dict[str, Any]
    ) -> str:
        """
        Log an action in the ChaosCore Proof of Agency system.
        
        Args:
            agent_id: ID of the agent performing the action
            action_type: Type of action (ANALYZE, CREATE, VERIFY, etc.)
            description: Description of the action
            data: Additional data about the action
            
        Returns:
            str: Action ID
        """
        # Convert string action_type to ActionType enum
        try:
            action_type_enum = ActionType[action_type.upper()]
        except KeyError:
            # Default to ANALYZE if not recognized
            action_type_enum = ActionType.ANALYZE
        
        # Log the action
        action_id = self._poa.log_action(
            agent_id=agent_id,
            action_type=action_type_enum,
            description=description,
            data=data
        )
        
        return action_id
    
    def verify_action(
        self,
        action_id: str,
        verifier_id: str,
        verification_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Verify an action in the ChaosCore Proof of Agency system.
        
        Args:
            action_id: ID of the action to verify
            verifier_id: ID of the agent performing the verification
            verification_data: Additional verification data
            
        Returns:
            bool: True if verification was successful
        """
        return self._poa.verify_action(
            action_id=action_id,
            verifier_id=verifier_id,
            verification_data=verification_data or {}
        )
    
    def record_outcome(
        self,
        action_id: str,
        success: bool,
        results: Dict[str, Any],
        impact_score: Optional[float] = None
    ) -> bool:
        """
        Record the outcome of an action in the ChaosCore Proof of Agency system.
        
        Args:
            action_id: ID of the action
            success: Whether the action was successful
            results: Results of the action
            impact_score: Optional impact score (0.0-1.0)
            
        Returns:
            bool: True if outcome was recorded successfully
        """
        return self._poa.record_outcome(
            action_id=action_id,
            success=success,
            results=results,
            impact_score=impact_score
        )
    
    def get_action(self, action_id: str) -> Optional[Dict[str, Any]]:
        """
        Get an action from the ChaosCore Proof of Agency system.
        
        Args:
            action_id: ID of the action
            
        Returns:
            Dict[str, Any]: Action data, or None if not found
        """
        action = self._poa.get_action(action_id)
        if action:
            return {
                "id": action.get_id(),
                "agent_id": action.get_agent_id(),
                "type": action.get_type().name,
                "description": action.get_description(),
                "data": action.get_data(),
                "status": action.get_status().name,
                "created_at": action.get_created_at()
            }
        return None
    
    def get_outcome(self, action_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the outcome of an action from the ChaosCore Proof of Agency system.
        
        Args:
            action_id: ID of the action
            
        Returns:
            Dict[str, Any]: Outcome data, or None if not found
        """
        outcome = self._poa.get_outcome(action_id)
        if outcome:
            return {
                "action_id": outcome.get_action_id(),
                "success": outcome.get_success(),
                "results": outcome.get_results(),
                "impact_score": outcome.get_impact_score(),
                "timestamp": outcome.get_timestamp()
            }
        return None
    
    def list_actions(
        self,
        agent_id: Optional[str] = None,
        action_type: Optional[str] = None
    ) -> List[str]:
        """
        List actions in the ChaosCore Proof of Agency system.
        
        Args:
            agent_id: Optional agent ID to filter by
            action_type: Optional action type to filter by
            
        Returns:
            List[str]: List of action IDs
        """
        # Convert string action_type to ActionType enum if provided
        action_type_enum = None
        if action_type:
            try:
                action_type_enum = ActionType[action_type.upper()]
            except KeyError:
                pass
        
        return self._poa.list_actions(
            agent_id=agent_id,
            action_type=action_type_enum
        )
    
    def anchor_action(self, action_id: str) -> bool:
        """
        Anchor an action in the blockchain.
        
        Args:
            action_id: ID of the action to anchor
            
        Returns:
            bool: True if anchoring was successful
        """
        return self._poa.anchor_action(action_id)
    
    def log_governance_action(
        self,
        agent_id: str,
        action_type: str,
        description: str,
        data: Dict[str, Any],
        verifier_id: Optional[str] = None,
        record_outcome: bool = False,
        outcome_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Log a governance action with optional verification and outcome recording.
        
        This is a convenience method that combines logging, verification, and outcome recording.
        
        Args:
            agent_id: ID of the agent performing the action
            action_type: Type of action (ANALYZE, CREATE, VERIFY, etc.)
            description: Description of the action
            data: Additional data about the action
            verifier_id: Optional ID of the agent performing the verification
            record_outcome: Whether to record an outcome
            outcome_data: Optional outcome data
            
        Returns:
            Dict[str, Any]: Action data including ID, verification status, and outcome if recorded
        """
        # Log the action
        action_id = self.log_action(
            agent_id=agent_id,
            action_type=action_type,
            description=description,
            data=data
        )
        
        result = {
            "action_id": action_id,
            "verified": False,
            "outcome_recorded": False
        }
        
        # Verify the action if verifier_id is provided
        if verifier_id:
            verification_data = {"timestamp": datetime.utcnow().isoformat()}
            result["verified"] = self.verify_action(
                action_id=action_id,
                verifier_id=verifier_id,
                verification_data=verification_data
            )
        
        # Record outcome if requested
        if record_outcome:
            outcome = outcome_data or {
                "success": True,
                "results": {"status": "completed"},
                "impact_score": 0.7
            }
            
            result["outcome_recorded"] = self.record_outcome(
                action_id=action_id,
                success=outcome.get("success", True),
                results=outcome.get("results", {}),
                impact_score=outcome.get("impact_score")
            )
            
            # Anchor the action if outcome was recorded
            if result["outcome_recorded"]:
                result["anchored"] = self.anchor_action(action_id)
        
        return result 