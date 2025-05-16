"""
Studio Framework Interfaces

This module defines the interfaces for the Studio Framework.
"""
import enum
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Set


class TaskStatus(enum.Enum):
    """Status of a task in a studio."""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskResult:
    """
    Represents the result of a task.
    
    A task result includes the output data, metadata, and status.
    """
    
    def get_task_id(self) -> str:
        """Get the ID of the task this result belongs to."""
        pass
    
    def get_status(self) -> TaskStatus:
        """Get the status of the task."""
        pass
    
    def get_output(self) -> Dict[str, Any]:
        """Get the output data of the task."""
        pass
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get the metadata of the task result."""
        pass
    
    def get_timestamp(self) -> datetime:
        """Get the timestamp when this result was created."""
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the task result to a dictionary."""
        pass
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaskResult':
        """Create a task result from a dictionary."""
        pass


class Task:
    """
    Represents a task in a studio.
    
    A task represents a unit of work that an agent can perform.
    """
    
    def get_id(self) -> str:
        """Get the unique identifier for this task."""
        pass
    
    def get_studio_id(self) -> str:
        """Get the ID of the studio this task belongs to."""
        pass
    
    def get_name(self) -> str:
        """Get the name of the task."""
        pass
    
    def get_description(self) -> str:
        """Get the description of the task."""
        pass
    
    def get_status(self) -> TaskStatus:
        """Get the status of the task."""
        pass
    
    def get_assigned_agent_id(self) -> Optional[str]:
        """Get the ID of the agent assigned to this task."""
        pass
    
    def get_inputs(self) -> Dict[str, Any]:
        """Get the inputs to this task."""
        pass
    
    def get_result(self) -> Optional[TaskResult]:
        """Get the result of this task."""
        pass
    
    def get_dependencies(self) -> List[str]:
        """Get the IDs of tasks that this task depends on."""
        pass
    
    def get_required_capabilities(self) -> Set[str]:
        """Get the capabilities required to perform this task."""
        pass
    
    def get_timeout(self) -> Optional[int]:
        """Get the timeout for this task in seconds."""
        pass
    
    def get_created_at(self) -> datetime:
        """Get the timestamp when this task was created."""
        pass
    
    def get_updated_at(self) -> datetime:
        """Get the timestamp when this task was last updated."""
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the task to a dictionary."""
        pass
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """Create a task from a dictionary."""
        pass
    
    def set_status(self, status: TaskStatus) -> None:
        """
        Set the status of the task.
        
        Args:
            status: The new status
        """
        pass
    
    def set_assigned_agent_id(self, agent_id: Optional[str]) -> None:
        """
        Set the agent assigned to this task.
        
        Args:
            agent_id: The ID of the agent, or None to unassign
        """
        pass
    
    def set_result(self, result: TaskResult) -> None:
        """
        Set the result of this task.
        
        Args:
            result: The task result
        """
        pass


class Studio(ABC):
    """
    Interface for a studio.
    
    A studio is a workspace for agents to collaborate on tasks.
    """
    
    @abstractmethod
    def get_id(self) -> str:
        """
        Get the unique identifier for this studio.
        
        Returns:
            str: The studio ID
        """
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """
        Get the name of this studio.
        
        Returns:
            str: The studio name
        """
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """
        Get the description of this studio.
        
        Returns:
            str: The studio description
        """
        pass
    
    @abstractmethod
    def add_task(
        self,
        name: str,
        description: str,
        inputs: Dict[str, Any],
        dependencies: Optional[List[str]] = None,
        required_capabilities: Optional[Set[str]] = None,
        timeout: Optional[int] = None
    ) -> Task:
        """
        Add a task to this studio.
        
        Args:
            name: The name of the task
            description: The description of the task
            inputs: The inputs to the task
            dependencies: Optional list of task IDs that this task depends on
            required_capabilities: Optional set of capabilities required to perform this task
            timeout: Optional timeout for this task in seconds
            
        Returns:
            Task: The created task
        """
        pass
    
    @abstractmethod
    def get_task(self, task_id: str) -> Task:
        """
        Get a task from this studio.
        
        Args:
            task_id: The ID of the task
            
        Returns:
            Task: The task
            
        Raises:
            TaskNotFoundException: If the task is not found
        """
        pass
    
    @abstractmethod
    def list_tasks(
        self,
        status: Optional[TaskStatus] = None,
        agent_id: Optional[str] = None
    ) -> List[Task]:
        """
        List tasks in this studio.
        
        Args:
            status: Optional status to filter by
            agent_id: Optional agent ID to filter by
            
        Returns:
            List[Task]: A list of tasks
        """
        pass
    
    @abstractmethod
    def assign_task(self, task_id: str, agent_id: str) -> Task:
        """
        Assign a task to an agent.
        
        Args:
            task_id: The ID of the task
            agent_id: The ID of the agent
            
        Returns:
            Task: The updated task
            
        Raises:
            TaskNotFoundException: If the task is not found
            InvalidTaskStateException: If the task cannot be assigned
        """
        pass
    
    @abstractmethod
    def start_task(self, task_id: str, agent_id: str) -> Task:
        """
        Start a task.
        
        Args:
            task_id: The ID of the task
            agent_id: The ID of the agent starting the task
            
        Returns:
            Task: The updated task
            
        Raises:
            TaskNotFoundException: If the task is not found
            InvalidTaskStateException: If the task cannot be started
        """
        pass
    
    @abstractmethod
    def complete_task(
        self,
        task_id: str,
        agent_id: str,
        outputs: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Task:
        """
        Complete a task.
        
        Args:
            task_id: The ID of the task
            agent_id: The ID of the agent completing the task
            outputs: The outputs of the task
            metadata: Optional metadata about the task completion
            
        Returns:
            Task: The updated task
            
        Raises:
            TaskNotFoundException: If the task is not found
            InvalidTaskStateException: If the task cannot be completed
        """
        pass
    
    @abstractmethod
    def fail_task(
        self,
        task_id: str,
        agent_id: str,
        reason: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Task:
        """
        Fail a task.
        
        Args:
            task_id: The ID of the task
            agent_id: The ID of the agent failing the task
            reason: The reason for the failure
            metadata: Optional metadata about the task failure
            
        Returns:
            Task: The updated task
            
        Raises:
            TaskNotFoundException: If the task is not found
            InvalidTaskStateException: If the task cannot be failed
        """
        pass
    
    @abstractmethod
    def cancel_task(self, task_id: str) -> Task:
        """
        Cancel a task.
        
        Args:
            task_id: The ID of the task
            
        Returns:
            Task: The updated task
            
        Raises:
            TaskNotFoundException: If the task is not found
            InvalidTaskStateException: If the task cannot be cancelled
        """
        pass
    
    @abstractmethod
    def get_next_task(
        self,
        agent_id: str,
        capabilities: Optional[Set[str]] = None
    ) -> Optional[Task]:
        """
        Get the next available task that an agent can perform.
        
        This method returns the next available task that:
        1. Is not assigned or in progress
        2. Has all dependencies completed
        3. Matches the agent's capabilities
        
        Args:
            agent_id: The ID of the agent
            capabilities: Optional set of capabilities that the agent has
            
        Returns:
            Optional[Task]: The next task, or None if no task is available
        """
        pass
    
    @abstractmethod
    def get_task_dependencies(self, task_id: str) -> List[Task]:
        """
        Get the dependencies of a task.
        
        Args:
            task_id: The ID of the task
            
        Returns:
            List[Task]: The dependencies of the task
            
        Raises:
            TaskNotFoundException: If the task is not found
        """
        pass
    
    @abstractmethod
    def get_task_dependents(self, task_id: str) -> List[Task]:
        """
        Get the tasks that depend on a task.
        
        Args:
            task_id: The ID of the task
            
        Returns:
            List[Task]: The tasks that depend on the task
            
        Raises:
            TaskNotFoundException: If the task is not found
        """
        pass


class StudioManager(ABC):
    """
    Interface for a studio manager.
    
    A studio manager is responsible for creating, retrieving, and managing studios.
    """
    
    @abstractmethod
    def create_studio(
        self,
        name: str,
        description: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Studio:
        """
        Create a new studio.
        
        Args:
            name: The name of the studio
            description: The description of the studio
            metadata: Optional metadata for the studio
            
        Returns:
            Studio: The created studio
        """
        pass
    
    @abstractmethod
    def get_studio(self, studio_id: str) -> Studio:
        """
        Get a studio by ID.
        
        Args:
            studio_id: The ID of the studio
            
        Returns:
            Studio: The studio
            
        Raises:
            StudioNotFoundException: If the studio is not found
        """
        pass
    
    @abstractmethod
    def list_studios(self) -> List[Studio]:
        """
        List all studios.
        
        Returns:
            List[Studio]: A list of studios
        """
        pass
    
    @abstractmethod
    def delete_studio(self, studio_id: str) -> None:
        """
        Delete a studio.
        
        Args:
            studio_id: The ID of the studio
            
        Raises:
            StudioNotFoundException: If the studio is not found
        """
        pass


# Exception classes
class StudioException(Exception):
    """Base exception for studio framework errors."""
    pass


class TaskNotFoundException(StudioException):
    """Exception raised when a task is not found."""
    pass


class InvalidTaskStateException(StudioException):
    """Exception raised when a task is in an invalid state for an operation."""
    pass


class StudioNotFoundException(StudioException):
    """Exception raised when a studio is not found."""
    pass 