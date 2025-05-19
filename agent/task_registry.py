"""
Task Registry for Governance Tasks

This module provides a central registry for all governance tasks that can be
executed by the governance agents.
"""

import logging
from typing import Dict, List, Optional, Type, Union, Any
from abc import ABC, abstractmethod
import uuid

logger = logging.getLogger(__name__)

class Task(ABC):
    """Abstract base class for governance tasks."""
    
    task_type: str = "generic"
    
    def __init__(self, task_id: Optional[str] = None, parameters: Optional[Dict[str, Any]] = None):
        """
        Initialize a governance task.
        
        Args:
            task_id: Unique identifier for the task, generated if not provided
            parameters: Task-specific parameters
        """
        self.task_id = task_id or f"task-{uuid.uuid4()}"
        self.parameters = parameters or {}
        
    @property
    def name(self) -> str:
        """Get the task name."""
        return self.__class__.__name__
    
    @property
    def description(self) -> str:
        """Get the task description."""
        return self.__doc__ or "No description available"
    
    @abstractmethod
    def requires(self) -> Dict[str, List[str]]:
        """
        Define the data requirements for this task.
        
        Returns:
            Dictionary mapping requirement categories to specific requirements
        """
        pass
    
    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the task with the given context.
        
        Args:
            context: Context data meeting the requirements
            
        Returns:
            Task execution results
        """
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the task to a dictionary representation."""
        return {
            "id": self.task_id,
            "name": self.name,
            "type": self.task_type,
            "description": self.description,
            "parameters": self.parameters,
            "requirements": self.requires()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """
        Create a task instance from a dictionary.
        
        Args:
            data: Dictionary representation of a task
            
        Returns:
            Task instance
        """
        # This would need to be handled by the registry or individual task types
        raise NotImplementedError("Task instances must be created by the registry")


class TaskRegistry:
    """Registry for governance tasks."""
    
    def __init__(self):
        """Initialize the task registry."""
        self._tasks: Dict[str, Type[Task]] = {}
        
    def register(self, task_class: Type[Task]) -> None:
        """
        Register a task class.
        
        Args:
            task_class: Task class to register
        """
        task_name = task_class.__name__
        logger.info(f"Registering task: {task_name}")
        self._tasks[task_name] = task_class
        
    def list_tasks(self) -> List[str]:
        """
        List all registered task names.
        
        Returns:
            List of registered task names
        """
        return list(self._tasks.keys())
    
    def get_task_class(self, task_name: str) -> Type[Task]:
        """
        Get a task class by name.
        
        Args:
            task_name: Task class name
            
        Returns:
            Task class
            
        Raises:
            KeyError: If task is not registered
        """
        if task_name not in self._tasks:
            raise KeyError(f"Task not registered: {task_name}")
        return self._tasks[task_name]
    
    def create_task(self, task_name: str, task_id: Optional[str] = None, 
                   parameters: Optional[Dict[str, Any]] = None) -> Task:
        """
        Create a task instance.
        
        Args:
            task_name: Task class name
            task_id: Unique identifier for the task
            parameters: Task-specific parameters
            
        Returns:
            Task instance
            
        Raises:
            KeyError: If task is not registered
        """
        task_class = self.get_task_class(task_name)
        return task_class(task_id=task_id, parameters=parameters)
    
    def find_tasks_for_requirements(self, requirements: Dict[str, List[str]]) -> List[str]:
        """
        Find tasks that match the given requirements.
        
        Args:
            requirements: Dictionary of requirement categories and specific requirements
            
        Returns:
            List of task names that can handle the requirements
        """
        matching_tasks = []
        
        for task_name, task_class in self._tasks.items():
            task_reqs = task_class(task_id=None).requires()
            
            # Check if the task can handle all the specified requirements
            matches_all = True
            for category, reqs in requirements.items():
                if category not in task_reqs:
                    matches_all = False
                    break
                    
                task_category_reqs = set(task_reqs[category])
                needed_reqs = set(reqs)
                
                # If the task doesn't support all the needed requirements in this category
                if not needed_reqs.issubset(task_category_reqs):
                    matches_all = False
                    break
                    
            if matches_all:
                matching_tasks.append(task_name)
                
        return matching_tasks

# Global instance
registry = TaskRegistry()

def register_task(task_class: Type[Task]) -> Type[Task]:
    """
    Decorator to register a task class.
    
    Args:
        task_class: Task class to register
        
    Returns:
        The registered task class
    """
    registry.register(task_class)
    return task_class 