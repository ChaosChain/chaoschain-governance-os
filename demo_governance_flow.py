#!/usr/bin/env python3
"""
Demo Governance Flow

This script demonstrates the end-to-end flow of the governance system using the ChaosCore platform components.
It registers governance agents, simulates a proposal, logs and verifies actions, anchors the results,
and updates reputation.
"""

import os
import sys
import json
import argparse
from datetime import datetime

from chaoscore.core.agent_registry import InMemoryAgentRegistry
from chaoscore.core.proof_of_agency import InMemoryProofOfAgency
from chaoscore.core.secure_execution import InMemorySecureExecution
from chaoscore.core.reputation import InMemoryReputationSystem
from chaoscore.core.studio import InMemoryStudioManager
from chaoscore.core.ethereum import EthereumClient

from adapters import (
    AgentRegistryAdapter,
    ProofOfAgencyAdapter,
    SecureExecutionAdapter,
    ReputationAdapter,
    StudioAdapter
)

from agent.agents.governance_agents_adapted import AdaptedGovernanceAgents
from simulation.secure_simulation import SecureSimulation


def create_adapters(use_ethereum=False):
    """
    Create the ChaosCore adapters.
    
    Args:
        use_ethereum: Whether to use Ethereum for anchoring
        
    Returns:
        Dictionary of adapters
    """
    # Create the core components
    agent_registry = InMemoryAgentRegistry()
    proof_of_agency = InMemoryProofOfAgency()
    secure_execution = InMemorySecureExecution()
    reputation_system = InMemoryReputationSystem()
    studio_manager = InMemoryStudioManager()
    
    # Create the adapters
    adapters = {
        "agent_registry": AgentRegistryAdapter(agent_registry),
        "proof_of_agency": ProofOfAgencyAdapter(proof_of_agency),
        "secure_execution": SecureExecutionAdapter(secure_execution),
        "reputation": ReputationAdapter(reputation_system),
        "studio": StudioAdapter(studio_manager)
    }
    
    # Initialize Ethereum client if needed
    if use_ethereum:
        # In a real implementation, use the actual contract address and provider
        ethereum_client = EthereumClient(
            contract_address="0x1234567890123456789012345678901234567890",
            provider_url=os.environ.get("ETHEREUM_PROVIDER_URL", "http://localhost:8545")
        )
        
        # Connect with the proof of agency adapter
        proof_of_agency.set_anchor_client(ethereum_client)
    
    return adapters


def run_governance_flow(use_ethereum=False, verbose=False):
    """
    Run the governance flow demo.
    
    Args:
        use_ethereum: Whether to use Ethereum for anchoring
        verbose: Enable verbose output
        
    Returns:
        Dictionary with results of the flow
    """
    print("Starting governance flow demo...")
    print(f"Using Ethereum for anchoring: {use_ethereum}")
    
    # Create adapters
    adapters = create_adapters(use_ethereum)
    
    # Create the governance agents
    print("\nCreating and registering governance agents...")
    governance_agents = AdaptedGovernanceAgents(
        agent_registry_adapter=adapters["agent_registry"],
        proof_of_agency_adapter=adapters["proof_of_agency"],
        secure_execution_adapter=adapters["secure_execution"],
        reputation_adapter=adapters["reputation"],
        studio_adapter=adapters["studio"],
        verbose=verbose
    )
    
    # Run the governance flow
    print("\nRunning governance flow...")
    start_time = datetime.now()
    result = governance_agents.run()
    end_time = datetime.now()
    
    # Print results
    print("\n" + "=" * 80)
    print(f"Governance flow completed in {(end_time - start_time).total_seconds():.2f} seconds")
    print("=" * 80)
    
    # Print agent IDs
    print("\nRegistered Agent IDs:")
    for role, agent_id in governance_agents.agent_ids.items():
        print(f"  {role}: {agent_id}")
    
    # Print action IDs
    print("\nAction Records:")
    for action_name, action_id in result["actions"].items():
        print(f"  {action_name}: {action_id}")
    
    # Print attestation
    print("\nAttestation:")
    print(f"  Hash: {result['attestation']['hash']}")
    
    # Print reputation changes
    if "reputation" in result and result["reputation"]:
        print("\nReputation Updates:")
        for role, update in result["reputation"].items():
            print(f"  {role}: {update['new_score'] - update['old_score']:.2f} (from {update['old_score']:.2f} to {update['new_score']:.2f})")
    
    # Print proposal summary
    print("\nProposal Summary:")
    if isinstance(result["proposal"], str):
        # Extract key points from the proposal text
        lines = result["proposal"].split("\n")
        for line in lines[:10]:  # Print first 10 lines
            if line.strip():
                print(f"  {line.strip()}")
        if len(lines) > 10:
            print("  ...")
    else:
        print(f"  {result['proposal']}")
    
    # Return the full result
    return result


def save_result(result, filename="governance_flow_result.json"):
    """
    Save the result to a file.
    
    Args:
        result: Result dictionary
        filename: Output filename
    """
    # Convert result to JSON-serializable format
    serializable_result = json.loads(json.dumps(result, default=str))
    
    # Save to file
    with open(filename, "w") as f:
        json.dump(serializable_result, f, indent=2)
    
    print(f"\nResult saved to {filename}")


def main():
    """Main function to run the demo."""
    parser = argparse.ArgumentParser(description="Demo of the governance flow using ChaosCore")
    parser.add_argument("--ethereum", action="store_true", help="Use Ethereum for anchoring")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--output", default="governance_flow_result.json", help="Output file for the result")
    args = parser.parse_args()
    
    try:
        result = run_governance_flow(use_ethereum=args.ethereum, verbose=args.verbose)
        save_result(result, args.output)
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main()) 