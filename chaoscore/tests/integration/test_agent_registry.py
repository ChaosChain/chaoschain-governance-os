"""
Integration tests for the Agent Registry.

These tests ensure that the Agent Registry components work together correctly.
"""
import json
import pytest
from datetime import datetime

from chaoscore.core.agent_registry.interfaces import AgentRegistryInterface, AgentNotFoundError
from chaoscore.core.agent_registry.implementation import InMemoryAgentRegistry, Agent
from chaoscore.core.ethereum.implementation import EthereumClient


def test_agent_registration_and_verification():
    """
    Test the complete agent registration and verification flow.
    
    This integration test covers:
    1. Registering an agent in the registry
    2. Verifying the agent exists
    3. Retrieving agent metadata
    4. Updating agent metadata
    5. Deactivating the agent
    """
    # Create a registry
    registry = InMemoryAgentRegistry()
    
    # Agent data
    public_key = "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
    metadata = {
        "name": "Test Integration Agent",
        "description": "Agent for integration testing",
        "capabilities": ["testing", "integration"],
        "domains": ["test-domain"],
        "custom_metadata": {
            "version": "1.0.0",
            "author": "ChaosCore Test Team"
        }
    }
    signature = "0xsignature"  # Mock signature (not validated in this implementation)
    
    # Register the agent
    agent_id = registry.register_agent(public_key, metadata, signature)
    
    # Verify the agent exists and is active
    assert registry.verify_agent(agent_id)
    
    # Get the agent's identity
    agent = registry.get_agent(agent_id)
    assert agent is not None
    assert agent.get_id() == agent_id
    assert agent.get_public_key() == public_key
    
    # Get the agent's metadata
    agent_metadata = registry.get_agent_metadata(agent_id)
    assert agent_metadata is not None
    assert agent_metadata.get_name() == metadata["name"]
    assert agent_metadata.get_description() == metadata["description"]
    assert set(agent_metadata.get_capabilities()) == set(metadata["capabilities"])
    assert set(agent_metadata.get_supported_domains()) == set(metadata["domains"])
    assert agent_metadata.get_custom_metadata() == metadata["custom_metadata"]
    
    # Update the agent's metadata
    updated_metadata = {
        "name": "Updated Integration Agent",
        "description": "Updated agent for integration testing",
        "capabilities": ["testing", "integration", "updated"],
        "domains": ["test-domain", "updated-domain"],
        "custom_metadata": {
            "version": "1.1.0",
            "author": "ChaosCore Test Team",
            "updated": True
        }
    }
    
    registry.update_metadata(agent_id, updated_metadata, signature)
    
    # Verify the update
    updated_agent_metadata = registry.get_agent_metadata(agent_id)
    assert updated_agent_metadata.get_name() == updated_metadata["name"]
    assert updated_agent_metadata.get_description() == updated_metadata["description"]
    assert set(updated_agent_metadata.get_capabilities()) == set(updated_metadata["capabilities"])
    assert set(updated_agent_metadata.get_supported_domains()) == set(updated_metadata["domains"])
    assert updated_agent_metadata.get_custom_metadata()["version"] == "1.1.0"
    assert updated_agent_metadata.get_custom_metadata()["updated"] is True
    
    # Deactivate the agent
    registry.deactivate_agent(agent_id, signature)
    
    # Verify the agent is no longer active
    assert not registry.verify_agent(agent_id)
    
    # The agent should still exist, just not be active
    agent = registry.get_agent(agent_id)
    assert agent is not None
    assert not agent.is_active()


def test_agent_registry_query_operations():
    """
    Test the query operations of the Agent Registry.
    
    This integration test covers:
    1. Registering multiple agents
    2. Querying agents by domain
    3. Querying agents by capability
    """
    # Create a registry
    registry = InMemoryAgentRegistry()
    
    # Register multiple agents with different capabilities and domains
    agents_data = [
        {
            "public_key": "0x1111111111111111111111111111111111111111111111111111111111111111",
            "metadata": {
                "name": "Agent 1",
                "description": "First test agent",
                "capabilities": ["capability-1", "capability-2"],
                "domains": ["domain-1", "domain-2"],
                "custom_metadata": {"id": 1}
            }
        },
        {
            "public_key": "0x2222222222222222222222222222222222222222222222222222222222222222",
            "metadata": {
                "name": "Agent 2",
                "description": "Second test agent",
                "capabilities": ["capability-2", "capability-3"],
                "domains": ["domain-2", "domain-3"],
                "custom_metadata": {"id": 2}
            }
        },
        {
            "public_key": "0x3333333333333333333333333333333333333333333333333333333333333333",
            "metadata": {
                "name": "Agent 3",
                "description": "Third test agent",
                "capabilities": ["capability-1", "capability-3", "capability-4"],
                "domains": ["domain-1", "domain-3", "domain-4"],
                "custom_metadata": {"id": 3}
            }
        }
    ]
    
    agent_ids = []
    for agent_data in agents_data:
        agent_id = registry.register_agent(
            agent_data["public_key"],
            agent_data["metadata"],
            "0xsignature"
        )
        agent_ids.append(agent_id)
    
    # All agents should be registered and active
    assert len(registry.list_agents()) == 3
    
    # Test querying by domain
    domain1_agents = registry.list_agents(domain="domain-1")
    assert len(domain1_agents) == 2
    assert agent_ids[0] in domain1_agents
    assert agent_ids[2] in domain1_agents
    
    domain2_agents = registry.list_agents(domain="domain-2")
    assert len(domain2_agents) == 2
    assert agent_ids[0] in domain2_agents
    assert agent_ids[1] in domain2_agents
    
    domain3_agents = registry.list_agents(domain="domain-3")
    assert len(domain3_agents) == 2
    assert agent_ids[1] in domain3_agents
    assert agent_ids[2] in domain3_agents
    
    domain4_agents = registry.list_agents(domain="domain-4")
    assert len(domain4_agents) == 1
    assert agent_ids[2] in domain4_agents
    
    # Test querying by capability
    capability1_agents = registry.list_agents(capability="capability-1")
    assert len(capability1_agents) == 2
    assert agent_ids[0] in capability1_agents
    assert agent_ids[2] in capability1_agents
    
    capability2_agents = registry.list_agents(capability="capability-2")
    assert len(capability2_agents) == 2
    assert agent_ids[0] in capability2_agents
    assert agent_ids[1] in capability2_agents
    
    capability3_agents = registry.list_agents(capability="capability-3")
    assert len(capability3_agents) == 2
    assert agent_ids[1] in capability3_agents
    assert agent_ids[2] in capability3_agents
    
    capability4_agents = registry.list_agents(capability="capability-4")
    assert len(capability4_agents) == 1
    assert agent_ids[2] in capability4_agents
    
    # Test querying by domain and capability
    # This isn't directly supported by our interface, but we could implement it
    
    # Test querying for non-existent domain/capability
    nonexistent_domain_agents = registry.list_agents(domain="nonexistent-domain")
    assert len(nonexistent_domain_agents) == 0
    
    nonexistent_capability_agents = registry.list_agents(capability="nonexistent-capability")
    assert len(nonexistent_capability_agents) == 0 