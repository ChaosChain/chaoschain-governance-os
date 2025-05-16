"""
Studio Adapter Implementation

This module implements the adapter for connecting the governance system to the ChaosCore
Studio Framework.
"""
from typing import Dict, Any, Optional, List, Set
from datetime import datetime

from chaoscore.core.studio import (
    Studio,
    StudioManager,
    Task,
    TaskStatus,
    TaskResult,
    StudioException
)


class StudioAdapter:
    """
    Adapter for the ChaosCore Studio Framework.
    
    This adapter provides methods for creating and managing studios, tasks, and workflows
    using the ChaosCore Studio Framework interfaces.
    """
    
    def __init__(self, studio_manager: StudioManager):
        """
        Initialize the studio adapter.
        
        Args:
            studio_manager: ChaosCore Studio Manager implementation
        """
        self._studio_manager = studio_manager
        self._active_studio = None
        self._studio_cache = {}  # Cache of studio IDs
    
    def create_governance_studio(
        self,
        name: str,
        description: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new governance studio.
        
        Args:
            name: Studio name
            description: Studio description
            metadata: Optional studio metadata
            
        Returns:
            Dict[str, Any]: Studio data
        """
        # Create the studio
        studio = self._studio_manager.create_studio(
            name=name,
            description=description,
            metadata=metadata or {}
        )
        
        # Set as active studio
        self._active_studio = studio
        
        # Cache the studio
        self._studio_cache[studio.get_id()] = studio
        
        return {
            "id": studio.get_id(),
            "name": studio.get_name(),
            "description": studio.get_description()
        }
    
    def get_studio(self, studio_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a studio by ID.
        
        Args:
            studio_id: Studio ID
            
        Returns:
            Dict[str, Any]: Studio data, or None if not found
        """
        try:
            studio = self._studio_manager.get_studio(studio_id)
            return {
                "id": studio.get_id(),
                "name": studio.get_name(),
                "description": studio.get_description()
            }
        except StudioException:
            return None
    
    def set_active_studio(self, studio_id: str) -> bool:
        """
        Set the active studio.
        
        Args:
            studio_id: Studio ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self._active_studio = self._studio_manager.get_studio(studio_id)
            return True
        except StudioException:
            return False
    
    def add_task(
        self,
        name: str,
        description: str,
        inputs: Dict[str, Any],
        dependencies: Optional[List[str]] = None,
        required_capabilities: Optional[Set[str]] = None,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Add a task to the active studio.
        
        Args:
            name: Task name
            description: Task description
            inputs: Task inputs
            dependencies: Optional list of dependency task IDs
            required_capabilities: Optional set of required capabilities
            timeout: Optional timeout in seconds
            
        Returns:
            Dict[str, Any]: Task data
        """
        if not self._active_studio:
            raise ValueError("No active studio set")
        
        # Add the task
        task = self._active_studio.add_task(
            name=name,
            description=description,
            inputs=inputs,
            dependencies=dependencies,
            required_capabilities=required_capabilities,
            timeout=timeout
        )
        
        return {
            "id": task.get_id(),
            "name": task.get_name(),
            "description": task.get_description(),
            "status": task.get_status().value,
            "inputs": task.get_inputs()
        }
    
    def assign_task(self, task_id: str, agent_id: str) -> Dict[str, Any]:
        """
        Assign a task to an agent.
        
        Args:
            task_id: Task ID
            agent_id: Agent ID
            
        Returns:
            Dict[str, Any]: Updated task data
        """
        if not self._active_studio:
            raise ValueError("No active studio set")
        
        # Assign the task
        task = self._active_studio.assign_task(task_id, agent_id)
        
        return {
            "id": task.get_id(),
            "name": task.get_name(),
            "status": task.get_status().value,
            "assigned_agent_id": task.get_assigned_agent_id()
        }
    
    def start_task(self, task_id: str, agent_id: str) -> Dict[str, Any]:
        """
        Start a task.
        
        Args:
            task_id: Task ID
            agent_id: Agent ID
            
        Returns:
            Dict[str, Any]: Updated task data
        """
        if not self._active_studio:
            raise ValueError("No active studio set")
        
        # Start the task
        task = self._active_studio.start_task(task_id, agent_id)
        
        return {
            "id": task.get_id(),
            "name": task.get_name(),
            "status": task.get_status().value,
            "assigned_agent_id": task.get_assigned_agent_id()
        }
    
    def complete_task(
        self,
        task_id: str,
        agent_id: str,
        outputs: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Complete a task.
        
        Args:
            task_id: Task ID
            agent_id: Agent ID
            outputs: Task outputs
            metadata: Optional task metadata
            
        Returns:
            Dict[str, Any]: Updated task data
        """
        if not self._active_studio:
            raise ValueError("No active studio set")
        
        # Complete the task
        task = self._active_studio.complete_task(
            task_id=task_id,
            agent_id=agent_id,
            outputs=outputs,
            metadata=metadata
        )
        
        return {
            "id": task.get_id(),
            "name": task.get_name(),
            "status": task.get_status().value,
            "assigned_agent_id": task.get_assigned_agent_id(),
            "result": {
                "outputs": task.get_result().get_output(),
                "metadata": task.get_result().get_metadata(),
                "timestamp": task.get_result().get_timestamp().isoformat()
            }
        }
    
    def create_proposal_workflow(
        self,
        agent_ids: Dict[str, str],
        proposal_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a governance proposal workflow.
        
        This is a convenience method that creates a studio and adds the necessary tasks
        for a governance proposal workflow.
        
        Args:
            agent_ids: Dictionary mapping agent roles to agent IDs
            proposal_data: Proposal data
            
        Returns:
            Dict[str, Any]: Workflow data including studio and task IDs
        """
        # Create a new studio for this workflow
        studio_name = f"Proposal Workflow - {datetime.utcnow().isoformat()}"
        studio_data = self.create_governance_studio(
            name=studio_name,
            description=f"Governance proposal workflow for {proposal_data.get('title', 'Untitled')}",
            metadata={"proposal_id": proposal_data.get("id")}
        )
        
        # Add research task
        research_task = self.add_task(
            name="Research Gas Metrics",
            description="Analyze Ethereum gas metrics to identify optimization opportunities",
            inputs={
                "metrics_source": proposal_data.get("metrics_source", "ethereum"),
                "num_blocks": proposal_data.get("num_blocks", 100)
            },
            required_capabilities={"data_analysis", "gas_metrics_analysis"}
        )
        
        # Add proposal development task
        proposal_task = self.add_task(
            name="Develop Parameter Proposal",
            description="Generate a parameter optimization proposal based on research findings",
            inputs={
                "research_task_id": research_task["id"],
                "proposal_template": proposal_data.get("template")
            },
            dependencies=[research_task["id"]],
            required_capabilities={"parameter_optimization", "simulation"}
        )
        
        # Add simulation task
        simulation_task = self.add_task(
            name="Simulate Proposal Effects",
            description="Simulate the effects of the proposed parameter changes",
            inputs={
                "proposal_task_id": proposal_task["id"],
                "simulation_config": proposal_data.get("simulation_config", {})
            },
            dependencies=[proposal_task["id"]],
            required_capabilities={"simulation"}
        )
        
        # Add verification task
        verification_task = self.add_task(
            name="Verify Simulation Results",
            description="Verify the simulation results of the proposed parameter changes",
            inputs={
                "simulation_task_id": simulation_task["id"]
            },
            dependencies=[simulation_task["id"]],
            required_capabilities={"verification"}
        )
        
        # Return workflow data
        return {
            "studio_id": studio_data["id"],
            "studio_name": studio_data["name"],
            "tasks": {
                "research": research_task["id"],
                "proposal": proposal_task["id"],
                "simulation": simulation_task["id"],
                "verification": verification_task["id"]
            },
            "agent_ids": agent_ids
        } 