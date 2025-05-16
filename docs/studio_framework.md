# ChaosCore Studio Framework

The Studio Framework is a core component of the ChaosChain Governance OS that enables the creation and management of collaborative agent workspaces for executing complex, multi-step tasks. This document explains the architecture, interfaces, and usage of the Studio Framework.

## Overview

The Studio Framework provides a structured environment for agents to collaborate on tasks by:
- Organizing tasks with clear dependencies
- Tracking task states throughout their lifecycle
- Matching tasks to agents based on capabilities
- Recording task results and metadata

A Studio is a workspace that contains a collection of tasks, and the Studio Manager is responsible for creating and managing studios.

## Architecture

The Studio Framework consists of the following components:

### TaskStatus

An enumeration that represents the status of a task:
- `PENDING`: The task is created but not yet assigned
- `ASSIGNED`: The task is assigned to an agent but not started
- `IN_PROGRESS`: The task is currently being worked on
- `COMPLETED`: The task is successfully completed
- `FAILED`: The task failed to complete
- `CANCELLED`: The task was cancelled

### TaskResult

Represents the result of a task, including:
- Output data
- Metadata
- Status
- Timestamp

### Task

Represents a unit of work that an agent can perform, including:
- Basic information (ID, name, description)
- Current status and assigned agent
- Inputs and result
- Dependencies on other tasks
- Required capabilities
- Timeout

### Studio

Interface for a workspace where agents collaborate on tasks. It provides methods to:
- Add tasks
- List tasks by status or agent
- Assign, start, complete, fail, or cancel tasks
- Navigate task dependencies
- Find the next available task for an agent

### StudioManager

Interface for creating, retrieving, and managing studios. It provides methods to:
- Create studios
- Get studios by ID
- List all studios
- Delete studios

### Implementations

- **BasicTaskResult**: Basic implementation of the TaskResult interface
- **BasicTask**: Basic implementation of the Task interface
- **BasicStudio**: Basic implementation of the Studio interface
- **InMemoryStudioManager**: In-memory implementation of the StudioManager interface

## Usage Examples

### Creating a Studio

```python
from chaoscore.core.studio import InMemoryStudioManager

# Create a studio manager
manager = InMemoryStudioManager()

# Create a studio
studio = manager.create_studio(
    name="Market Analysis Studio",
    description="A studio for market analysis tasks",
    metadata={"domain": "finance", "owner": "research_team"}
)

print(f"Created studio with ID: {studio.get_id()}")
```

### Adding Tasks to a Studio

```python
# Add a task with no dependencies
data_collection_task = studio.add_task(
    name="Collect Market Data",
    description="Collect historical market data for analysis",
    inputs={
        "symbols": ["BTC", "ETH", "SOL"],
        "timeframe": "1d",
        "period": "3mo"
    }
)

# Add a task that depends on the first task
analysis_task = studio.add_task(
    name="Analyze Market Data",
    description="Perform technical analysis on collected data",
    inputs={
        "indicators": ["RSI", "MACD", "Bollinger Bands"],
        "parameters": {"rsi_period": 14, "macd_fast": 12, "macd_slow": 26}
    },
    dependencies=[data_collection_task.get_id()],
    required_capabilities={"technical_analysis"}
)

# Add a task with multiple dependencies and a timeout
report_task = studio.add_task(
    name="Generate Analysis Report",
    description="Create a comprehensive analysis report",
    inputs={
        "format": "pdf",
        "include_charts": True
    },
    dependencies=[analysis_task.get_id()],
    required_capabilities={"report_generation"},
    timeout=300  # seconds
)
```

### Task Workflow

```python
# Get all pending tasks
pending_tasks = studio.list_tasks(status=TaskStatus.PENDING)

# Assign a task to an agent
data_collection_task_id = data_collection_task.get_id()
agent_id = "data_collector_agent"

studio.assign_task(data_collection_task_id, agent_id)

# Start the task
studio.start_task(data_collection_task_id, agent_id)

# Complete the task with outputs and metadata
studio.complete_task(
    task_id=data_collection_task_id,
    agent_id=agent_id,
    outputs={
        "collected_data": {
            "BTC": [...],
            "ETH": [...],
            "SOL": [...]
        }
    },
    metadata={
        "processing_time": 2.34,
        "data_points": 90
    }
)

# If a task fails
# studio.fail_task(
#     task_id=data_collection_task_id,
#     agent_id=agent_id,
#     reason="Failed to fetch data: API rate limit exceeded",
#     metadata={"error_code": 429}
# )

# If a task needs to be cancelled
# studio.cancel_task(data_collection_task_id)
```

### Finding Tasks for Agents

```python
# Get the next available task for an agent
agent_id = "analyst_agent"
agent_capabilities = {"technical_analysis", "statistical_analysis"}

next_task = studio.get_next_task(agent_id, capabilities=agent_capabilities)

if next_task:
    print(f"Next task for agent: {next_task.get_name()}")
    print(f"Description: {next_task.get_description()}")
    print(f"Inputs: {next_task.get_inputs()}")
    
    # Assign and start the task
    studio.assign_task(next_task.get_id(), agent_id)
    studio.start_task(next_task.get_id(), agent_id)
else:
    print("No tasks available for the agent")
```

### Working with Task Dependencies

```python
# Get the dependencies of a task
task_id = report_task.get_id()
dependencies = studio.get_task_dependencies(task_id)

print(f"Task {task_id} depends on:")
for dep in dependencies:
    print(f"- {dep.get_name()} (Status: {dep.get_status().value})")

# Get the tasks that depend on a task
data_task_id = data_collection_task.get_id()
dependents = studio.get_task_dependents(data_task_id)

print(f"Tasks that depend on {data_task_id}:")
for dep in dependents:
    print(f"- {dep.get_name()} (Status: {dep.get_status().value})")
```

## Integration with Other Components

The Studio Framework integrates with other ChaosCore components:

### Agent Registry

The Studio Framework uses the Agent Registry to:
- Verify agent identities
- Get agent capabilities

### Proof of Agency

The Studio Framework can work with the Proof of Agency framework to:
- Record task executions as agent actions
- Verify and anchor task results
- Compute rewards based on task completion

### Secure Execution Environment

The Studio Framework can use the Secure Execution Environment to:
- Execute task code securely
- Generate attestations for task execution
- Verify task results

## Best Practices

1. **Task Design**:
   - Break down complex workflows into smaller, focused tasks
   - Design clear task dependencies to avoid deadlocks
   - Include all necessary inputs in the task definition

2. **Agent Capabilities**:
   - Define capabilities that accurately reflect agent skills
   - Match tasks to agents with appropriate capabilities
   - Consider capability hierarchies (e.g., "advanced_math" implies "basic_math")

3. **Error Handling**:
   - Implement proper error handling for task failures
   - Consider retry mechanisms for transient failures
   - Design fallback tasks when critical tasks fail

4. **Monitoring**:
   - Monitor task status and completion rates
   - Track task execution times and resource usage
   - Alert on task failures or timeouts

5. **Scaling**:
   - Distribute tasks across multiple agents for parallelism
   - Prioritize critical path tasks to minimize overall completion time
   - Balance workload across available agents 