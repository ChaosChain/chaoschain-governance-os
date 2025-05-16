"""
Agent Registry Demo

This script demonstrates how to use the Agent Registry component of ChaosCore.
"""
import sys
import os
import json
from typing import Dict, Any

# Add the parent directory to sys.path to import chaoscore
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from chaoscore.core.agent_registry import (
    InMemoryAgentRegistry,
    MockOnChainRegistry,
    AgentNotFoundError,
    DuplicateAgentError
)


def create_mock_agent_metadata(name: str, domain: str) -> Dict[str, Any]:
    """Create mock metadata for an agent."""
    return {
        "name": name,
        "description": f"A demo agent specializing in {domain}",
        "capabilities": ["analyze", "propose", "verify"],
        "domains": [domain],
        "custom_metadata": {
            "model": "gpt-4",
            "version": "1.0.0",
            "creator": "ChaosCore Demo"
        }
    }


def print_section(title: str):
    """Print a section title."""
    print("\n" + "=" * 50)
    print(f" {title} ".center(50, "-"))
    print("=" * 50 + "\n")


def main():
    print_section("Agent Registry Demo")
    
    # Initialize the registry components
    registry = InMemoryAgentRegistry()
    on_chain_registry = MockOnChainRegistry(registry)
    
    print("Initialized Agent Registry and On-Chain Registry")
    
    # Register some agents
    print("\nRegistering agents...")
    
    # Governance agent
    gov_metadata = create_mock_agent_metadata("Governance Agent", "blockchain-governance")
    gov_public_key = "04e68acfc0253a10620dff706b0a1b1f1f5833ea3beb3bde2250d5f271f3563f772caa6555159b9cc19a6c1691ca9e2972898c24220acce71eb09cbf538440add"
    try:
        gov_id = registry.register_agent(gov_public_key, gov_metadata, "mock_signature")
        print(f"Registered governance agent with ID: {gov_id}")
    except DuplicateAgentError as e:
        print(f"Error: {e}")
    
    # Finance agent
    finance_metadata = create_mock_agent_metadata("Finance Agent", "defi-optimization")
    finance_public_key = "0461aac28f22d0679abdd7a26a3fa565ee3c3873c0bf9702dce30d0c32e3265a5c1565b179f88c2f01f9c0abc6d53f4fef97d9aaff1a2f99c7e8b95bca01ba6d68"
    try:
        finance_id = registry.register_agent(finance_public_key, finance_metadata, "mock_signature")
        print(f"Registered finance agent with ID: {finance_id}")
    except DuplicateAgentError as e:
        print(f"Error: {e}")
    
    # Science agent
    science_metadata = create_mock_agent_metadata("Science Agent", "research-coordination")
    science_public_key = "04a28af54f313a2e7c73c05295982129a28654789560c3e3f1dc0bb3dcf39f89b2c25f9c389547a94323daa306b7d73c8b2d0f22ed99ddea1c58b9e5ed3ff0561"
    try:
        science_id = registry.register_agent(science_public_key, science_metadata, "mock_signature")
        print(f"Registered science agent with ID: {science_id}")
    except DuplicateAgentError as e:
        print(f"Error: {e}")
    
    # List all agents
    print_section("All Registered Agents")
    all_agents = registry.list_agents()
    print(f"Found {len(all_agents)} agents:")
    for agent_id in all_agents:
        agent = registry.get_agent(agent_id)
        print(f"- {agent.get_name()} ({agent_id[:8]}...)")
    
    # Filter agents by domain
    print_section("Filtering Agents by Domain")
    domain = "blockchain-governance"
    domain_agents = registry.list_agents(domain=domain)
    print(f"Agents in domain '{domain}':")
    for agent_id in domain_agents:
        agent = registry.get_agent(agent_id)
        print(f"- {agent.get_name()} ({agent_id[:8]}...)")
    
    # Get agent metadata
    print_section("Agent Metadata")
    try:
        gov_agent = registry.get_agent(gov_id)
        print(f"Agent: {gov_agent.get_name()}")
        print(f"Description: {gov_agent.get_description()}")
        print(f"Capabilities: {', '.join(gov_agent.get_capabilities())}")
        print(f"Domains: {', '.join(gov_agent.get_supported_domains())}")
        print(f"Custom Metadata: {json.dumps(gov_agent.get_custom_metadata(), indent=2)}")
    except AgentNotFoundError as e:
        print(f"Error: {e}")
    
    # On-chain anchoring
    print_section("On-Chain Anchoring")
    try:
        # Anchor the governance agent's identity on-chain
        tx_hash = on_chain_registry.anchor_identity(gov_id)
        print(f"Anchored governance agent on-chain with transaction: {tx_hash}")
        
        # Verify anchoring
        is_anchored = on_chain_registry.verify_anchoring(gov_id)
        print(f"Is governance agent anchored on-chain? {is_anchored}")
        
        # Get on-chain data
        on_chain_data = on_chain_registry.get_on_chain_data(gov_id)
        print(f"On-chain data: {json.dumps(on_chain_data, indent=2)}")
        
        # Update on-chain data
        update_data = {"reputation_score": 95, "verified": True}
        update_tx = on_chain_registry.update_on_chain_data(gov_id, update_data, "mock_signature")
        print(f"Updated on-chain data with transaction: {update_tx}")
        
        # Get updated on-chain data
        updated_data = on_chain_registry.get_on_chain_data(gov_id)
        print(f"Updated on-chain data: {json.dumps(updated_data, indent=2)}")
    except (AgentNotFoundError, AnchoringError) as e:
        print(f"Error: {e}")
    
    # Update agent metadata
    print_section("Updating Agent Metadata")
    try:
        # Update the governance agent's metadata
        updated_metadata = {
            "description": "An enhanced governance agent with policy expertise",
            "capabilities": ["analyze", "propose", "verify", "simulate", "monitor"],
            "custom_metadata": {
                "model": "gpt-4-turbo",
                "version": "2.0.0"
            }
        }
        registry.update_metadata(gov_id, updated_metadata, "mock_signature")
        print("Updated governance agent metadata")
        
        # Get updated metadata
        updated_agent = registry.get_agent(gov_id)
        print(f"Agent: {updated_agent.get_name()}")
        print(f"Description: {updated_agent.get_description()}")
        print(f"Capabilities: {', '.join(updated_agent.get_capabilities())}")
        print(f"Domains: {', '.join(updated_agent.get_supported_domains())}")
        print(f"Custom Metadata: {json.dumps(updated_agent.get_custom_metadata(), indent=2)}")
    except AgentNotFoundError as e:
        print(f"Error: {e}")
    
    # Deactivate an agent
    print_section("Deactivating an Agent")
    try:
        # Deactivate the science agent
        registry.deactivate_agent(science_id, "mock_signature")
        print(f"Deactivated science agent")
        
        # List active agents
        active_agents = registry.list_agents()
        print(f"Active agents after deactivation:")
        for agent_id in active_agents:
            agent = registry.get_agent(agent_id)
            print(f"- {agent.get_name()} ({agent_id[:8]}...)")
        
        # Verify the science agent is deactivated
        is_active = registry.verify_agent(science_id)
        print(f"Is science agent active? {is_active}")
    except AgentNotFoundError as e:
        print(f"Error: {e}")
    
    print_section("Demo Complete")


if __name__ == "__main__":
    main() 