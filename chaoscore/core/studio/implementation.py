"""
Studio Framework Implementations

This module provides implementations of the Studio Framework interfaces.
"""
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Set, Tuple
from collections import defaultdict

from .interfaces import (
    Studio,
    StudioManager,
    Task,
    TaskResult,
    TaskStatus,
    TaskNotFoundException,
    InvalidTaskStateException,
    StudioNotFoundException
)


class BasicTaskResult(TaskResult):
    """
    Basic implementation of TaskResult.
    """
    
    def __init__(
        self,
        task_id: str,
        status: TaskStatus,
        output: Dict[str, Any],
        metadata: Dict[str, Any],
        timestamp: datetime
    ):
        self._task_id = task_id
        self._status = status
        self._output = output
        self._metadata = metadata
        self._timestamp = timestamp
    
    def get_task_id(self) -> str:
        return self._task_id
    
    def get_status(self) -> TaskStatus:
        return self._status
    
    def get_output(self) -> Dict[str, Any]:
        return self._output.copy()
    
    def get_metadata(self) -> Dict[str, Any]:
        return self._metadata.copy()
    
    def get_timestamp(self) -> datetime:
        return self._timestamp
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self._task_id,
            "status": self._status.value,
            "output": self._output,
            "metadata": self._metadata,
            "timestamp": self._timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BasicTaskResult':
        return cls(
            task_id=data["task_id"],
            status=TaskStatus(data["status"]),
            output=data["output"],
            metadata=data["metadata"],
            timestamp=datetime.fromisoformat(data["timestamp"])
        )


class BasicTask(Task):
    """
    Basic implementation of Task.
    """
    
    def __init__(
        self,
        task_id: str,
        studio_id: str,
        name: str,
        description: str,
        inputs: Dict[str, Any],
        dependencies: List[str],
        required_capabilities: Set[str],
        timeout: Optional[int],
        created_at: datetime,
        updated_at: datetime,
        status: TaskStatus = TaskStatus.PENDING,
        assigned_agent_id: Optional[str] = None,
        result: Optional[TaskResult] = None
    ):
        self._id = task_id
        self._studio_id = studio_id
        self._name = name
        self._description = description
        self._inputs = inputs
        self._dependencies = dependencies
        self._required_capabilities = required_capabilities
        self._timeout = timeout
        self._created_at = created_at
        self._updated_at = updated_at
        self._status = status
        self._assigned_agent_id = assigned_agent_id
        self._result = result
    
    def get_id(self) -> str:
        return self._id
    
    def get_studio_id(self) -> str:
        return self._studio_id
    
    def get_name(self) -> str:
        return self._name
    
    def get_description(self) -> str:
        return self._description
    
    def get_status(self) -> TaskStatus:
        return self._status
    
    def get_assigned_agent_id(self) -> Optional[str]:
        return self._assigned_agent_id
    
    def get_inputs(self) -> Dict[str, Any]:
        return self._inputs.copy()
    
    def get_result(self) -> Optional[TaskResult]:
        return self._result
    
    def get_dependencies(self) -> List[str]:
        return self._dependencies.copy()
    
    def get_required_capabilities(self) -> Set[str]:
        return self._required_capabilities.copy()
    
    def get_timeout(self) -> Optional[int]:
        return self._timeout
    
    def get_created_at(self) -> datetime:
        return self._created_at
    
    def get_updated_at(self) -> datetime:
        return self._updated_at
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "id": self._id,
            "studio_id": self._studio_id,
            "name": self._name,
            "description": self._description,
            "status": self._status.value,
            "assigned_agent_id": self._assigned_agent_id,
            "inputs": self._inputs,
            "dependencies": self._dependencies,
            "required_capabilities": list(self._required_capabilities),
            "timeout": self._timeout,
            "created_at": self._created_at.isoformat(),
            "updated_at": self._updated_at.isoformat()
        }
        
        if self._result:
            result["result"] = self._result.to_dict()
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BasicTask':
        result = None
        if "result" in data and data["result"]:
            result = BasicTaskResult.from_dict(data["result"])
        
        return cls(
            task_id=data["id"],
            studio_id=data["studio_id"],
            name=data["name"],
            description=data["description"],
            inputs=data["inputs"],
            dependencies=data["dependencies"],
            required_capabilities=set(data["required_capabilities"]),
            timeout=data["timeout"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            status=TaskStatus(data["status"]),
            assigned_agent_id=data["assigned_agent_id"],
            result=result
        )
    
    def set_status(self, status: TaskStatus) -> None:
        self._status = status
        self._updated_at = datetime.now()
    
    def set_assigned_agent_id(self, agent_id: Optional[str]) -> None:
        self._assigned_agent_id = agent_id
        self._updated_at = datetime.now()
    
    def set_result(self, result: TaskResult) -> None:
        self._result = result
        self._updated_at = datetime.now()


class BasicStudio(Studio):
    """
    Basic implementation of Studio.
    """
    
    def __init__(
        self,
        studio_id: str,
        name: str,
        description: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self._id = studio_id
        self._name = name
        self._description = description
        self._metadata = metadata or {}
        self._tasks = {}  # task_id -> Task
        self._dependency_map = defaultdict(list)  # task_id -> list of dependent task IDs
    
    def get_id(self) -> str:
        return self._id
    
    def get_name(self) -> str:
        return self._name
    
    def get_description(self) -> str:
        return self._description
    
    def add_task(
        self,
        name: str,
        description: str,
        inputs: Dict[str, Any],
        dependencies: Optional[List[str]] = None,
        required_capabilities: Optional[Set[str]] = None,
        timeout: Optional[int] = None
    ) -> Task:
        # Validate dependencies
        deps = dependencies or []
        for dep_id in deps:
            if dep_id not in self._tasks:
                raise TaskNotFoundException(f"Dependency task {dep_id} not found")
        
        # Create a new task
        task_id = str(uuid.uuid4())
        now = datetime.now()
        
        task = BasicTask(
            task_id=task_id,
            studio_id=self._id,
            name=name,
            description=description,
            inputs=inputs,
            dependencies=deps,
            required_capabilities=required_capabilities or set(),
            timeout=timeout,
            created_at=now,
            updated_at=now
        )
        
        # Add the task to the studio
        self._tasks[task_id] = task
        
        # Update dependency map
        for dep_id in deps:
            self._dependency_map[dep_id].append(task_id)
        
        return task
    
    def get_task(self, task_id: str) -> Task:
        if task_id not in self._tasks:
            raise TaskNotFoundException(f"Task {task_id} not found")
        
        return self._tasks[task_id]
    
    def list_tasks(
        self,
        status: Optional[TaskStatus] = None,
        agent_id: Optional[str] = None
    ) -> List[Task]:
        tasks = list(self._tasks.values())
        
        # Filter by status
        if status:
            tasks = [task for task in tasks if task.get_status() == status]
        
        # Filter by agent ID
        if agent_id:
            tasks = [task for task in tasks if task.get_assigned_agent_id() == agent_id]
        
        return tasks
    
    def assign_task(self, task_id: str, agent_id: str) -> Task:
        task = self.get_task(task_id)
        
        # Check if the task can be assigned
        if task.get_status() != TaskStatus.PENDING:
            raise InvalidTaskStateException(
                f"Task {task_id} cannot be assigned (current status: {task.get_status().value})"
            )
        
        # Assign the task
        task.set_status(TaskStatus.ASSIGNED)
        task.set_assigned_agent_id(agent_id)
        
        return task
    
    def start_task(self, task_id: str, agent_id: str) -> Task:
        task = self.get_task(task_id)
        
        # Check if the task can be started
        if task.get_status() != TaskStatus.ASSIGNED:
            raise InvalidTaskStateException(
                f"Task {task_id} cannot be started (current status: {task.get_status().value})"
            )
        
        # Check if the task is assigned to the given agent
        if task.get_assigned_agent_id() != agent_id:
            raise InvalidTaskStateException(
                f"Task {task_id} is not assigned to agent {agent_id}"
            )
        
        # Check if all dependencies are completed
        for dep_id in task.get_dependencies():
            dep_task = self.get_task(dep_id)
            if dep_task.get_status() != TaskStatus.COMPLETED:
                raise InvalidTaskStateException(
                    f"Task {task_id} cannot be started because dependency {dep_id} is not completed"
                )
        
        # Start the task
        task.set_status(TaskStatus.IN_PROGRESS)
        
        return task
    
    def complete_task(
        self,
        task_id: str,
        agent_id: str,
        outputs: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Task:
        task = self.get_task(task_id)
        
        # Check if the task can be completed
        if task.get_status() != TaskStatus.IN_PROGRESS:
            raise InvalidTaskStateException(
                f"Task {task_id} cannot be completed (current status: {task.get_status().value})"
            )
        
        # Check if the task is assigned to the given agent
        if task.get_assigned_agent_id() != agent_id:
            raise InvalidTaskStateException(
                f"Task {task_id} is not assigned to agent {agent_id}"
            )
        
        # Create a result
        result = BasicTaskResult(
            task_id=task_id,
            status=TaskStatus.COMPLETED,
            output=outputs,
            metadata=metadata or {},
            timestamp=datetime.now()
        )
        
        # Complete the task
        task.set_status(TaskStatus.COMPLETED)
        task.set_result(result)
        
        return task
    
    def fail_task(
        self,
        task_id: str,
        agent_id: str,
        reason: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Task:
        task = self.get_task(task_id)
        
        # Check if the task can be failed
        if task.get_status() not in [TaskStatus.ASSIGNED, TaskStatus.IN_PROGRESS]:
            raise InvalidTaskStateException(
                f"Task {task_id} cannot be failed (current status: {task.get_status().value})"
            )
        
        # Check if the task is assigned to the given agent
        if task.get_assigned_agent_id() != agent_id:
            raise InvalidTaskStateException(
                f"Task {task_id} is not assigned to agent {agent_id}"
            )
        
        # Create a result
        meta = metadata or {}
        meta["reason"] = reason
        
        result = BasicTaskResult(
            task_id=task_id,
            status=TaskStatus.FAILED,
            output={},
            metadata=meta,
            timestamp=datetime.now()
        )
        
        # Fail the task
        task.set_status(TaskStatus.FAILED)
        task.set_result(result)
        
        return task
    
    def cancel_task(self, task_id: str) -> Task:
        task = self.get_task(task_id)
        
        # Check if the task can be cancelled
        if task.get_status() in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
            raise InvalidTaskStateException(
                f"Task {task_id} cannot be cancelled (current status: {task.get_status().value})"
            )
        
        # Cancel the task
        task.set_status(TaskStatus.CANCELLED)
        
        # Create a result
        result = BasicTaskResult(
            task_id=task_id,
            status=TaskStatus.CANCELLED,
            output={},
            metadata={"reason": "cancelled"},
            timestamp=datetime.now()
        )
        
        task.set_result(result)
        
        return task
    
    def get_next_task(
        self,
        agent_id: str,
        capabilities: Optional[Set[str]] = None
    ) -> Optional[Task]:
        # Get all pending tasks
        pending_tasks = self.list_tasks(status=TaskStatus.PENDING)
        
        # Filter tasks by capabilities
        if capabilities:
            pending_tasks = [
                task for task in pending_tasks
                if len(task.get_required_capabilities() - capabilities) == 0
            ]
        
        # Filter tasks by dependencies
        available_tasks = []
        for task in pending_tasks:
            all_deps_completed = True
            for dep_id in task.get_dependencies():
                dep_task = self.get_task(dep_id)
                if dep_task.get_status() != TaskStatus.COMPLETED:
                    all_deps_completed = False
                    break
            
            if all_deps_completed:
                available_tasks.append(task)
        
        # Return the first available task, if any
        return available_tasks[0] if available_tasks else None
    
    def get_task_dependencies(self, task_id: str) -> List[Task]:
        task = self.get_task(task_id)
        
        return [self.get_task(dep_id) for dep_id in task.get_dependencies()]
    
    def get_task_dependents(self, task_id: str) -> List[Task]:
        self.get_task(task_id)  # Ensure the task exists
        
        dependent_ids = self._dependency_map.get(task_id, [])
        return [self.get_task(dep_id) for dep_id in dependent_ids]


class InMemoryStudioManager(StudioManager):
    """
    In-memory implementation of StudioManager.
    """
    
    def __init__(self):
        self._studios = {}  # studio_id -> Studio
    
    def create_studio(
        self,
        name: str,
        description: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Studio:
        studio_id = str(uuid.uuid4())
        
        studio = BasicStudio(
            studio_id=studio_id,
            name=name,
            description=description,
            metadata=metadata
        )
        
        self._studios[studio_id] = studio
        
        return studio
    
    def get_studio(self, studio_id: str) -> Studio:
        if studio_id not in self._studios:
            raise StudioNotFoundException(f"Studio {studio_id} not found")
        
        return self._studios[studio_id]
    
    def list_studios(self) -> List[Studio]:
        return list(self._studios.values())
    
    def delete_studio(self, studio_id: str) -> None:
        if studio_id not in self._studios:
            raise StudioNotFoundException(f"Studio {studio_id} not found")
        
        del self._studios[studio_id] 