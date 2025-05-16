# ChaosCore Python SDK

This package provides a high-level Python SDK for interacting with the ChaosCore platform.

## Installation

You can install the SDK directly from the repository:

```bash
pip install -e chaoscore/sdk/python
```

## Usage

### Basic Usage

```python
from chaoscore.sdk.python import ChaosCoreClient

# Create the ChaosCore client
client = ChaosCoreClient()

# Register an agent
agent_id = client.register_agent(
    name="My Agent",
    email="agent@example.com",
    metadata={"role": "developer"}
)

# Log an action
action_id = client.log_action(
    agent_id=agent_id,
    action_type="CREATE",
    description="Create a new proposal",
    data={"proposal_id": "123"}
)

# Record an outcome
client.record_outcome(
    action_id=action_id,
    success=True,
    results={"proposal": "Gas limit optimization"},
    impact_score=0.8
)

# Run a function in the secure execution environment
def secure_function(param1, param2):
    return {"result": param1 + param2}

result = client.run_secure(secure_function, 1, 2)
print(result)  # {"result": 3, "attestation": {...}}
```

### Governance Features

```python
# Run a governance simulation
proposal_data = {
    "id": "prop-123",
    "title": "Gas Limit Optimization",
    "parameters": {
        "gas_limit": 20000000,
        "base_fee_max_change_denominator": 10
    }
}

simulation_result = client.run_governance_simulation(
    proposal_data=proposal_data,
    agent_id=agent_id
)

print(simulation_result)
```

### CrewAI Integration

```python
from chaoscore.sdk.python import ChaosCoreClient, CrewAIAdapter
from crewai import Agent, Crew, Task

# Create the ChaosCore client
client = ChaosCoreClient()

# Create the CrewAI adapter
adapter = CrewAIAdapter(client)

# Create CrewAI agents
researcher = Agent(
    role="Gas Metrics Researcher",
    goal="Analyze Ethereum gas metrics",
    backstory="You are an expert in Ethereum gas mechanics"
)

developer = Agent(
    role="Parameter Optimizer",
    goal="Create optimized parameter proposals",
    backstory="You are a blockchain protocol developer"
)

# Create tasks
research_task = Task(
    description="Analyze Ethereum gas metrics",
    agent=researcher
)

proposal_task = Task(
    description="Create parameter optimization proposal",
    agent=developer,
    context=[research_task]
)

# Create crew
crew = Crew(
    agents=[researcher, developer],
    tasks=[research_task, proposal_task]
)

# Run the crew with ChaosCore integration
result = adapter.run_crew(crew)
print(result)
```

## Features

- Agent Registration and Management
- Action Logging and Verification
- Secure Execution Environment
- Governance Simulation
- CrewAI Integration

## Development

To set up the development environment:

```bash
# Clone the repository
git clone https://github.com/chaoschain/chaoscore.git

# Install the SDK in development mode
cd chaoscore
pip install -e sdk/python

# Run the example
python sdk/python/examples/governance_example.py
``` 