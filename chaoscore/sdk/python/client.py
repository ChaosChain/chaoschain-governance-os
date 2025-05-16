"""
ChaosCore Client

This module provides the main client for interacting with the ChaosCore platform.
"""
import os
from typing import Dict, Any, Optional, List

from chaoscore.core.agent_registry import InMemoryAgentRegistry, AgentRegistryInterface
from chaoscore.core.proof_of_agency import InMemoryProofOfAgency, ProofOfAgencyInterface
from chaoscore.core.secure_execution import InMemorySecureExecution, SecureExecutionEnvironment
from chaoscore.core.reputation import InMemoryReputationSystem
from chaoscore.core.studio import InMemoryStudioManager


class ChaosCoreClient:
    """
    Main client for interacting with the ChaosCore platform.
    """
    
    def __init__(
        self,
        agent_registry: Optional[AgentRegistryInterface] = None,
        proof_of_agency: Optional[ProofOfAgencyInterface] = None,
        secure_execution: Optional[SecureExecutionEnvironment] = None,
        use_remote: bool = False,
        remote_url: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        """
        Initialize the ChaosCore client.
        
        Args:
            agent_registry: Optional agent registry implementation
            proof_of_agency: Optional proof of agency implementation
            secure_execution: Optional secure execution implementation
            use_remote: Whether to use remote services
            remote_url: URL of the remote ChaosCore API
            api_key: API key for authentication
        """
        self.use_remote = use_remote
        self.remote_url = remote_url or os.environ.get("CHAOSCORE_API_URL")
        self.api_key = api_key or os.environ.get("CHAOSCORE_API_KEY")
        
        if use_remote and not self.remote_url:
            raise ValueError("Remote URL is required when use_remote is True")
        
        # Initialize components
        self._agent_registry = agent_registry or InMemoryAgentRegistry()
        self._proof_of_agency = proof_of_agency or InMemoryProofOfAgency()
        self._secure_execution = secure_execution or InMemorySecureExecution()
        self._reputation_system = InMemoryReputationSystem()
        self._studio_manager = InMemoryStudioManager()
    
    # Agent Registry methods
    
    def register_agent(self, name: str, email: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Register a new agent.
        
        Args:
            name: Agent name
            email: Agent email
            metadata: Optional agent metadata
            
        Returns:
            Agent ID
        """
        if self.use_remote:
            # In a real implementation, this would call the remote API
            pass
        else:
            return self._agent_registry.register_agent(name, email, metadata or {})
    
    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Get agent information.
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Agent information
        """
        if self.use_remote:
            # In a real implementation, this would call the remote API
            pass
        else:
            agent = self._agent_registry.get_agent(agent_id)
            if agent:
                return {
                    "id": agent.get_id(),
                    "name": agent.get_name(),
                    "email": agent.get_email(),
                    "metadata": agent.get_metadata()
                }
            return None
    
    # Proof of Agency methods
    
    def log_action(
        self,
        agent_id: str,
        action_type: str,
        description: str,
        data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Log an action.
        
        Args:
            agent_id: Agent ID
            action_type: Type of action
            description: Action description
            data: Optional action data
            
        Returns:
            Action ID
        """
        if self.use_remote:
            # In a real implementation, this would call the remote API
            pass
        else:
            return self._proof_of_agency.log_action(
                agent_id=agent_id,
                action_type=action_type,
                description=description,
                data=data or {}
            )
    
    def record_outcome(
        self,
        action_id: str,
        success: bool,
        results: Optional[Dict[str, Any]] = None,
        impact_score: float = 0.0
    ) -> bool:
        """
        Record the outcome of an action.
        
        Args:
            action_id: Action ID
            success: Whether the action was successful
            results: Optional action results
            impact_score: Impact score of the action
            
        Returns:
            Whether the outcome was recorded successfully
        """
        if self.use_remote:
            # In a real implementation, this would call the remote API
            pass
        else:
            return self._proof_of_agency.record_outcome(
                action_id=action_id,
                success=success,
                results=results or {},
                impact_score=impact_score
            )
    
    # Secure Execution methods
    
    def run_secure(self, func, *args, **kwargs) -> Dict[str, Any]:
        """
        Run a function in the secure execution environment.
        
        Args:
            func: Function to run
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Dictionary with result and attestation
        """
        if self.use_remote:
            # In a real implementation, this would call the remote API
            pass
        else:
            return self._secure_execution.run(func, *args, **kwargs)
    
    # Governance methods
    
    def run_governance_simulation(
        self,
        proposal_data: Dict[str, Any],
        agent_id: str,
        simulation_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Run a governance simulation.
        
        This is a convenience method that combines several core operations:
        1. Logs the simulation action
        2. Runs the simulation in the secure execution environment
        3. Records the outcome
        
        Args:
            proposal_data: Proposal data to simulate
            agent_id: ID of the agent running the simulation
            simulation_params: Optional simulation parameters
            
        Returns:
            Dictionary with simulation results, action ID, and attestation
        """
        # Log the simulation action
        action_id = self.log_action(
            agent_id=agent_id,
            action_type="SIMULATE",
            description=f"Simulate proposal: {proposal_data.get('title', 'Unnamed')}",
            data={"proposal_id": proposal_data.get("id", "unknown")}
        )
        
        # Define the simulation function
        def _simulate_proposal(proposal_data, **kwargs):
            # In a real implementation, this would use a proper simulation engine
            return {
                "simulation_id": "sim-" + action_id,
                "proposal_id": proposal_data.get("id", "unknown"),
                "result": "success",
                "parameters": proposal_data.get("parameters", {})
            }
        
        # Run the simulation in the secure execution environment
        simulation_result = self.run_secure(
            _simulate_proposal,
            proposal_data=proposal_data,
            **(simulation_params or {})
        )
        
        # Record the outcome
        self.record_outcome(
            action_id=action_id,
            success=True,
            results={"simulation": simulation_result.get("result", {})},
            impact_score=0.8
        )
        
        # Return the results
        return {
            "action_id": action_id,
            "simulation": simulation_result.get("result", {}),
            "attestation": simulation_result.get("attestation", {})
        } 