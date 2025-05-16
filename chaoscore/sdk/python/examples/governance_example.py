#!/usr/bin/env python3
"""
Governance Example

This script demonstrates how to use the ChaosCore SDK for governance scenarios.
"""

import json
import sys
import uuid
from pathlib import Path

# Add parent directory to path to import the SDK
sys.path.append(str(Path(__file__).parent.parent.parent.parent.parent))

from chaoscore.sdk.python import ChaosCoreClient


def main():
    """Run the governance example."""
    print("ChaosCore Governance SDK Example")
    print("================================")
    
    # Create the ChaosCore client
    client = ChaosCoreClient()
    
    # Register an agent
    print("\nRegistering agent...")
    agent_id = client.register_agent(
        name="Parameter Optimizer",
        email=f"optimizer-{uuid.uuid4()}@chaoscore.ai",
        metadata={
            "role": "developer",
            "expertise": "gas optimization",
            "version": "1.0.0"
        }
    )
    print(f"Agent registered with ID: {agent_id}")
    
    # Get agent information
    print("\nGetting agent information...")
    agent_info = client.get_agent(agent_id)
    print(f"Agent name: {agent_info['name']}")
    print(f"Agent email: {agent_info['email']}")
    print(f"Agent metadata: {agent_info['metadata']}")
    
    # Create a proposal
    proposal_data = {
        "id": str(uuid.uuid4()),
        "title": "Gas Limit Optimization Proposal",
        "description": "Proposal to increase the gas limit to improve throughput",
        "parameters": {
            "gas_limit": 20000000,
            "base_fee_max_change_denominator": 10,
            "simulation_blocks": 100
        }
    }
    print("\nCreated proposal:")
    print(f"ID: {proposal_data['id']}")
    print(f"Title: {proposal_data['title']}")
    print(f"Parameters: {proposal_data['parameters']}")
    
    # Run the governance simulation
    print("\nRunning governance simulation...")
    simulation_result = client.run_governance_simulation(
        proposal_data=proposal_data,
        agent_id=agent_id
    )
    print(f"Simulation action ID: {simulation_result['action_id']}")
    print(f"Attestation hash: {simulation_result['attestation'].get('hash')}")
    
    # Save the results to a file
    output_file = "governance_example_result.json"
    with open(output_file, "w") as f:
        json.dump(simulation_result, f, indent=2, default=str)
    print(f"\nResults saved to {output_file}")


if __name__ == "__main__":
    main() 