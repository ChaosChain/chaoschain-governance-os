# Governance Studio Framework

This document provides an architectural overview of the ChaosChain Governance Studio and explains how to use it for governance proposal development, simulation, and verification.

## Architecture Overview

The Governance Studio builds on the ChaosCore platform components to provide a secure, verifiable, and reputation-aware environment for blockchain governance. The diagram below illustrates the architecture:

```
┌─────────────────────────────────────────────────────────────────────┐
│                      Governance Studio Framework                     │
└─────────────────────────────────────────────────────────────────────┘
              │                 │                 │
              ▼                 ▼                 ▼
┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
│   Agent-Based   │   │   Secure Flow   │   │  Verification   │
│ Proposal System │   │    Execution    │   │   & Anchoring   │
└─────────────────┘   └─────────────────┘   └─────────────────┘
         │                    │                     │
         ▼                    ▼                     ▼
┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
│                 │   │                 │   │                 │
│ Agent Registry  │   │     Secure      │   │    Proof of     │
│                 │   │    Execution    │   │     Agency      │
└─────────────────┘   └─────────────────┘   └─────────────────┘
         │                    │                     │
         └────────────────────┼─────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │                 │
                    │   Reputation    │
                    │     System      │
                    │                 │
                    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │                 │
                    │    Ethereum     │
                    │    Anchoring    │
                    │                 │
                    └─────────────────┘
```

### Key Components

1. **Agent-Based Proposal System**: Uses CrewAI to orchestrate specialized agents (researchers, developers) that analyze data and generate parameter optimization proposals.

2. **Secure Flow Execution**: Runs proposal simulations and critical operations in a trusted execution environment with attestations.

3. **Verification & Anchoring**: Provides mechanisms to verify operations, record outcomes, and anchor results on Ethereum.

4. **Reputation System**: Tracks agent performance over time, adjusting reputation scores based on outcome quality and verification.

## Usage

### Setting Up the Environment

The Governance Studio uses adapters to connect to the ChaosCore platform components:

```python
from chaoscore.core.agent_registry import InMemoryAgentRegistry
from chaoscore.core.proof_of_agency import InMemoryProofOfAgency
from chaoscore.core.secure_execution import InMemorySecureExecution
from chaoscore.core.reputation import InMemoryReputationSystem
from chaoscore.core.studio import InMemoryStudioManager

from adapters import (
    AgentRegistryAdapter,
    ProofOfAgencyAdapter,
    SecureExecutionAdapter,
    ReputationAdapter,
    StudioAdapter
)

# Create components
agent_registry = InMemoryAgentRegistry()
proof_of_agency = InMemoryProofOfAgency()
secure_execution = InMemorySecureExecution()
reputation_system = InMemoryReputationSystem()
studio_manager = InMemoryStudioManager()

# Create adapters
adapters = {
    "agent_registry": AgentRegistryAdapter(agent_registry),
    "proof_of_agency": ProofOfAgencyAdapter(proof_of_agency),
    "secure_execution": SecureExecutionAdapter(secure_execution),
    "reputation": ReputationAdapter(reputation_system),
    "studio": StudioAdapter(studio_manager)
}
```

### Running a Governance Workflow

To run a governance workflow:

```python
from agent.agents.governance_agents_adapted import AdaptedGovernanceAgents

# Create governance agents
governance_agents = AdaptedGovernanceAgents(
    agent_registry_adapter=adapters["agent_registry"],
    proof_of_agency_adapter=adapters["proof_of_agency"],
    secure_execution_adapter=adapters["secure_execution"],
    reputation_adapter=adapters["reputation"],
    studio_adapter=adapters["studio"]
)

# Run the workflow
result = governance_agents.run()
```

### Result Structure

The result contains:

```python
{
    "analysis": "Detailed gas metrics analysis...",
    "proposal": "Parameter optimization proposal...",
    "simulation": {
        "simulation_config": { ... },
        "baseline": { ... },
        "modified": { ... },
        "comparison": { ... },
        "analysis": { ... }
    },
    "actions": {
        "research_action_id": "action-uuid-1",
        "proposal_action_id": "action-uuid-2"
    },
    "attestation": {
        "hash": "attestation-hash",
        "data": { ... }
    },
    "reputation": {
        "researcher": {
            "old_score": 0.5,
            "new_score": 0.7,
            "delta": 0.2
        },
        "developer": {
            "old_score": 0.5,
            "new_score": 0.8,
            "delta": 0.3
        }
    }
}
```

## CLI Commands

The Governance Studio includes a demo script that shows the full workflow:

```bash
# Run the demo with in-memory components
python demo_governance_flow.py

# Run with Ethereum anchoring (requires Ethereum provider URL)
python demo_governance_flow.py --ethereum

# Run with verbose output
python demo_governance_flow.py --verbose

# Specify output file
python demo_governance_flow.py --output result.json
```

## Integration with Existing Systems

The Governance Studio can be integrated with existing systems by:

1. Using the adapter layer to connect to existing data sources and systems
2. Customizing the agents to use domain-specific tools and models
3. Extending the workflow to include additional steps or agents

## Custom Agent Capabilities

You can extend the Governance Studio with custom agent capabilities:

1. Create a new agent class that inherits from CrewAI's Agent
2. Implement domain-specific tools and methods
3. Register the agent with the Agent Registry
4. Update the workflow to include the new agent

## Performance and Scaling

The Governance Studio can be scaled by:

1. Using distributed execution for simulations
2. Employing parallel agent execution for independent tasks
3. Scaling the storage backends (e.g., using PostgreSQL instead of in-memory storage)
4. Adding caching layers for frequently accessed data

## Security Considerations

The Governance Studio enhances security through:

1. Attestation of critical operations via the Secure Execution Environment
2. Verification of actions through the Proof of Agency framework
3. On-chain anchoring of results for immutable record-keeping
4. Reputation tracking to identify and privilege trusted agents

## API Reference

For detailed API reference, see the in-code documentation in the following modules:

- `agent.agents.governance_agents_adapted`: The adapted governance agents class
- `adapters`: The adapter layer connecting to ChaosCore components
- `simulation.secure_simulation`: The secure simulation environment 