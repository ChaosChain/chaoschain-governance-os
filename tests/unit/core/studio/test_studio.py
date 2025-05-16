"""
Unit tests for the Studio Framework.
"""
import pytest
from datetime import datetime
from typing import Set

from chaoscore.core.studio import (
    TaskStatus,
    TaskResult,
    BasicTaskResult,
    BasicTask,
    BasicStudio,
    InMemoryStudioManager,
    TaskNotFoundException,
    InvalidTaskStateException,
    StudioNotFoundException
)


class TestBasicTaskResult:
    """Test the BasicTaskResult implementation"""
    
    def test_init_and_getters(self):
        """Test initialization and getter methods"""
        task_id = "task_123"
        status = TaskStatus.COMPLETED
        output = {"result": "success", "value": 42}
        metadata = {"duration": 3.14, "metrics": {"accuracy": 0.95}}
        timestamp = datetime.now()
        
        result = BasicTaskResult(
            task_id=task_id,
            status=status,
            output=output,
            metadata=metadata,
            timestamp=timestamp
        )
        
        assert result.get_task_id() == task_id
        assert result.get_status() == status
        assert result.get_output() == output
        assert result.get_metadata() == metadata
        assert result.get_timestamp() == timestamp
    
    def test_to_dict_and_from_dict(self):
        """Test to_dict and from_dict methods"""
        original = BasicTaskResult(
            task_id="task_123",
            status=TaskStatus.COMPLETED,
            output={"result": "success", "value": 42},
            metadata={"duration": 3.14, "metrics": {"accuracy": 0.95}},
            timestamp=datetime.fromisoformat("2023-01-01T12:00:00")
        )
        
        # Convert to dict and back
        result_dict = original.to_dict()
        reconstructed = BasicTaskResult.from_dict(result_dict)
        
        # Verify all properties are preserved
        assert original.get_task_id() == reconstructed.get_task_id()
        assert original.get_status() == reconstructed.get_status()
        assert original.get_output() == reconstructed.get_output()
        assert original.get_metadata() == reconstructed.get_metadata()
        assert original.get_timestamp().isoformat() == reconstructed.get_timestamp().isoformat()


class TestBasicTask:
    """Test the BasicTask implementation"""
    
    def test_init_and_getters(self):
        """Test initialization and getter methods"""
        task_id = "task_123"
        studio_id = "studio_456"
        name = "Test Task"
        description = "A test task"
        inputs = {"param1": "value1", "param2": 42}
        dependencies = ["dep_1", "dep_2"]
        required_capabilities = {"capability1", "capability2"}
        timeout = 60
        created_at = datetime.now()
        updated_at = datetime.now()
        status = TaskStatus.PENDING
        assigned_agent_id = None
        
        task = BasicTask(
            task_id=task_id,
            studio_id=studio_id,
            name=name,
            description=description,
            inputs=inputs,
            dependencies=dependencies,
            required_capabilities=required_capabilities,
            timeout=timeout,
            created_at=created_at,
            updated_at=updated_at,
            status=status,
            assigned_agent_id=assigned_agent_id
        )
        
        assert task.get_id() == task_id
        assert task.get_studio_id() == studio_id
        assert task.get_name() == name
        assert task.get_description() == description
        assert task.get_inputs() == inputs
        assert task.get_dependencies() == dependencies
        assert task.get_required_capabilities() == required_capabilities
        assert task.get_timeout() == timeout
        assert task.get_created_at() == created_at
        assert task.get_updated_at() == updated_at
        assert task.get_status() == status
        assert task.get_assigned_agent_id() == assigned_agent_id
        assert task.get_result() is None
    
    def test_setter_methods(self):
        """Test setter methods"""
        task = BasicTask(
            task_id="task_123",
            studio_id="studio_456",
            name="Test Task",
            description="A test task",
            inputs={},
            dependencies=[],
            required_capabilities=set(),
            timeout=None,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Test set_status
        task.set_status(TaskStatus.ASSIGNED)
        assert task.get_status() == TaskStatus.ASSIGNED
        
        # Test set_assigned_agent_id
        task.set_assigned_agent_id("agent_789")
        assert task.get_assigned_agent_id() == "agent_789"
        
        # Test set_result
        result = BasicTaskResult(
            task_id=task.get_id(),
            status=TaskStatus.COMPLETED,
            output={"result": "success"},
            metadata={},
            timestamp=datetime.now()
        )
        task.set_result(result)
        assert task.get_result() == result
    
    def test_to_dict_and_from_dict(self):
        """Test to_dict and from_dict methods"""
        now = datetime.fromisoformat("2023-01-01T12:00:00")
        
        original = BasicTask(
            task_id="task_123",
            studio_id="studio_456",
            name="Test Task",
            description="A test task",
            inputs={"param1": "value1", "param2": 42},
            dependencies=["dep_1", "dep_2"],
            required_capabilities={"capability1", "capability2"},
            timeout=60,
            created_at=now,
            updated_at=now,
            status=TaskStatus.ASSIGNED,
            assigned_agent_id="agent_789"
        )
        
        # Add a result
        result = BasicTaskResult(
            task_id=original.get_id(),
            status=TaskStatus.COMPLETED,
            output={"result": "success"},
            metadata={},
            timestamp=now
        )
        original.set_result(result)
        
        # Convert to dict and back
        task_dict = original.to_dict()
        reconstructed = BasicTask.from_dict(task_dict)
        
        # Verify all properties are preserved
        assert original.get_id() == reconstructed.get_id()
        assert original.get_studio_id() == reconstructed.get_studio_id()
        assert original.get_name() == reconstructed.get_name()
        assert original.get_description() == reconstructed.get_description()
        assert original.get_inputs() == reconstructed.get_inputs()
        assert original.get_dependencies() == reconstructed.get_dependencies()
        assert original.get_required_capabilities() == reconstructed.get_required_capabilities()
        assert original.get_timeout() == reconstructed.get_timeout()
        assert original.get_created_at().isoformat() == reconstructed.get_created_at().isoformat()
        assert original.get_updated_at().isoformat() == reconstructed.get_updated_at().isoformat()
        assert original.get_status() == reconstructed.get_status()
        assert original.get_assigned_agent_id() == reconstructed.get_assigned_agent_id()
        
        # Verify result is preserved
        assert reconstructed.get_result() is not None
        assert reconstructed.get_result().get_task_id() == result.get_task_id()
        assert reconstructed.get_result().get_status() == result.get_status()
        assert reconstructed.get_result().get_output() == result.get_output()


class TestBasicStudio:
    """Test the BasicStudio implementation"""
    
    @pytest.fixture
    def studio(self):
        """Create a BasicStudio for testing"""
        return BasicStudio(
            studio_id="studio_123",
            name="Test Studio",
            description="A test studio",
            metadata={"owner": "test_user"}
        )
    
    def test_init_and_getters(self, studio):
        """Test initialization and getter methods"""
        assert studio.get_id() == "studio_123"
        assert studio.get_name() == "Test Studio"
        assert studio.get_description() == "A test studio"
    
    def test_add_task(self, studio):
        """Test adding a task to the studio"""
        task = studio.add_task(
            name="Test Task",
            description="A test task",
            inputs={"param1": "value1"}
        )
        
        assert task is not None
        assert task.get_studio_id() == studio.get_id()
        assert task.get_name() == "Test Task"
        assert task.get_description() == "A test task"
        assert task.get_inputs() == {"param1": "value1"}
        assert task.get_status() == TaskStatus.PENDING
    
    def test_add_task_with_dependencies(self, studio):
        """Test adding a task with dependencies"""
        # Add first task
        task1 = studio.add_task(
            name="Task 1",
            description="First task",
            inputs={}
        )
        
        # Add second task depending on first
        task2 = studio.add_task(
            name="Task 2",
            description="Second task",
            inputs={},
            dependencies=[task1.get_id()]
        )
        
        assert task2.get_dependencies() == [task1.get_id()]
        
        # Verify dependency relationship
        dependencies = studio.get_task_dependencies(task2.get_id())
        assert len(dependencies) == 1
        assert dependencies[0].get_id() == task1.get_id()
        
        dependents = studio.get_task_dependents(task1.get_id())
        assert len(dependents) == 1
        assert dependents[0].get_id() == task2.get_id()
    
    def test_get_task(self, studio):
        """Test getting a task from the studio"""
        # Add a task
        original = studio.add_task(
            name="Test Task",
            description="A test task",
            inputs={}
        )
        
        # Get the task
        task = studio.get_task(original.get_id())
        
        assert task is not None
        assert task.get_id() == original.get_id()
        
        # Test getting a non-existent task
        with pytest.raises(TaskNotFoundException):
            studio.get_task("non_existent_task")
    
    def test_list_tasks(self, studio):
        """Test listing tasks in the studio"""
        # Add some tasks
        task1 = studio.add_task(name="Task 1", description="First task", inputs={})
        task2 = studio.add_task(name="Task 2", description="Second task", inputs={})
        
        # Assign one task
        studio.assign_task(task1.get_id(), "agent_1")
        
        # List all tasks
        all_tasks = studio.list_tasks()
        assert len(all_tasks) == 2
        
        # List pending tasks
        pending_tasks = studio.list_tasks(status=TaskStatus.PENDING)
        assert len(pending_tasks) == 1
        assert pending_tasks[0].get_id() == task2.get_id()
        
        # List assigned tasks
        assigned_tasks = studio.list_tasks(status=TaskStatus.ASSIGNED)
        assert len(assigned_tasks) == 1
        assert assigned_tasks[0].get_id() == task1.get_id()
        
        # List tasks by agent
        agent_tasks = studio.list_tasks(agent_id="agent_1")
        assert len(agent_tasks) == 1
        assert agent_tasks[0].get_id() == task1.get_id()
    
    def test_task_workflow(self, studio):
        """Test the full task workflow (assign, start, complete)"""
        # Add a task
        task = studio.add_task(
            name="Workflow Task",
            description="A task for workflow testing",
            inputs={"data": "test_data"}
        )
        
        task_id = task.get_id()
        agent_id = "test_agent"
        
        # Assign the task
        task = studio.assign_task(task_id, agent_id)
        assert task.get_status() == TaskStatus.ASSIGNED
        assert task.get_assigned_agent_id() == agent_id
        
        # Start the task
        task = studio.start_task(task_id, agent_id)
        assert task.get_status() == TaskStatus.IN_PROGRESS
        
        # Complete the task
        outputs = {"result": "success", "processed_data": "processed_test_data"}
        metadata = {"processing_time": 1.23}
        
        task = studio.complete_task(task_id, agent_id, outputs, metadata)
        assert task.get_status() == TaskStatus.COMPLETED
        
        # Verify result
        result = task.get_result()
        assert result is not None
        assert result.get_status() == TaskStatus.COMPLETED
        assert result.get_output() == outputs
        assert result.get_metadata() == metadata
    
    def test_fail_task(self, studio):
        """Test failing a task"""
        # Add and start a task
        task = studio.add_task(
            name="Failing Task",
            description="A task that will fail",
            inputs={}
        )
        
        task_id = task.get_id()
        agent_id = "test_agent"
        
        studio.assign_task(task_id, agent_id)
        studio.start_task(task_id, agent_id)
        
        # Fail the task
        reason = "Test failure reason"
        metadata = {"error_code": 500}
        
        task = studio.fail_task(task_id, agent_id, reason, metadata)
        assert task.get_status() == TaskStatus.FAILED
        
        # Verify result
        result = task.get_result()
        assert result is not None
        assert result.get_status() == TaskStatus.FAILED
        assert "reason" in result.get_metadata()
        assert result.get_metadata()["reason"] == reason
        assert "error_code" in result.get_metadata()
        assert result.get_metadata()["error_code"] == 500
    
    def test_cancel_task(self, studio):
        """Test cancelling a task"""
        # Add a task
        task = studio.add_task(
            name="Cancelled Task",
            description="A task that will be cancelled",
            inputs={}
        )
        
        task_id = task.get_id()
        
        # Cancel the task
        task = studio.cancel_task(task_id)
        assert task.get_status() == TaskStatus.CANCELLED
        
        # Verify result
        result = task.get_result()
        assert result is not None
        assert result.get_status() == TaskStatus.CANCELLED
        assert "reason" in result.get_metadata()
        assert result.get_metadata()["reason"] == "cancelled"
    
    def test_get_next_task(self, studio):
        """Test getting the next available task"""
        # Add tasks with dependencies
        task1 = studio.add_task(
            name="Task 1",
            description="First task",
            inputs={}
        )
        
        task2 = studio.add_task(
            name="Task 2",
            description="Second task with dependency",
            inputs={},
            dependencies=[task1.get_id()]
        )
        
        task3 = studio.add_task(
            name="Task 3",
            description="Third task with capabilities",
            inputs={},
            required_capabilities={"advanced_math"}
        )
        
        # Get next task for an agent with no special capabilities
        next_task = studio.get_next_task("agent_1")
        assert next_task is not None
        assert next_task.get_id() == task1.get_id()
        
        # Get next task for an agent with capabilities
        next_task = studio.get_next_task("agent_2", capabilities={"advanced_math"})
        assert next_task is not None
        assert next_task.get_id() in [task1.get_id(), task3.get_id()]
        
        # Complete task1
        studio.assign_task(task1.get_id(), "agent_1")
        studio.start_task(task1.get_id(), "agent_1")
        studio.complete_task(task1.get_id(), "agent_1", {"result": "success"})
        
        # Get next task
        next_task = studio.get_next_task("agent_1")
        assert next_task is not None
        assert next_task.get_id() == task2.get_id()


class TestInMemoryStudioManager:
    """Test the InMemoryStudioManager implementation"""
    
    @pytest.fixture
    def manager(self):
        """Create an InMemoryStudioManager for testing"""
        return InMemoryStudioManager()
    
    def test_create_studio(self, manager):
        """Test creating a studio"""
        studio = manager.create_studio(
            name="Test Studio",
            description="A test studio",
            metadata={"owner": "test_user"}
        )
        
        assert studio is not None
        assert studio.get_name() == "Test Studio"
        assert studio.get_description() == "A test studio"
    
    def test_get_studio(self, manager):
        """Test getting a studio"""
        # Create a studio
        original = manager.create_studio(
            name="Test Studio",
            description="A test studio"
        )
        
        # Get the studio
        studio = manager.get_studio(original.get_id())
        
        assert studio is not None
        assert studio.get_id() == original.get_id()
        
        # Test getting a non-existent studio
        with pytest.raises(StudioNotFoundException):
            manager.get_studio("non_existent_studio")
    
    def test_list_studios(self, manager):
        """Test listing studios"""
        # Create some studios
        studio1 = manager.create_studio(name="Studio 1", description="First studio")
        studio2 = manager.create_studio(name="Studio 2", description="Second studio")
        
        # List all studios
        studios = manager.list_studios()
        
        assert len(studios) == 2
        assert any(s.get_id() == studio1.get_id() for s in studios)
        assert any(s.get_id() == studio2.get_id() for s in studios)
    
    def test_delete_studio(self, manager):
        """Test deleting a studio"""
        # Create a studio
        studio = manager.create_studio(
            name="Test Studio",
            description="A test studio"
        )
        
        # Delete the studio
        manager.delete_studio(studio.get_id())
        
        # Verify it's deleted
        with pytest.raises(StudioNotFoundException):
            manager.get_studio(studio.get_id())
        
        # Test deleting a non-existent studio
        with pytest.raises(StudioNotFoundException):
            manager.delete_studio("non_existent_studio") 