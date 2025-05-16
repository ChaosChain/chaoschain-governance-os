"""
Unit tests for the Agent Registry component.
"""
import json
import pytest
from datetime import datetime

from chaoscore.core.agent_registry.interfaces import AgentRegistryInterface, AgentNotFoundError, DuplicateAgentError
from chaoscore.core.agent_registry.implementation import InMemoryAgentRegistry, Agent


def test_agent_identity():
    """Test the Agent identity functionality."""
    # Create an agent
    agent = Agent(
        agent_id="test-id",
        public_key="0x1234567890abcdef",
        name="Test Agent",
        description="A test agent",
        capabilities=["test"],
        domains=["test-domain"],
        created_at=datetime.now(),
        updated_at=datetime.now(),
        custom_metadata={"test": "value"}
    )
    
    # Check identity methods
    assert agent.get_id() == "test-id"
    assert agent.get_public_key() == "0x1234567890abcdef"
    assert agent.verify_signature(b"test", b"signature")  # This is a mock that always returns True


def test_agent_metadata():
    """Test the Agent metadata functionality."""
    # Create an agent
    now = datetime.now()
    custom_metadata = {"test": "value", "number": 42}
    agent = Agent(
        agent_id="test-id",
        public_key="0x1234567890abcdef",
        name="Test Agent",
        description="A test agent",
        capabilities=["test1", "test2"],
        domains=["domain1", "domain2"],
        created_at=now,
        updated_at=now,
        custom_metadata=custom_metadata
    )
    
    # Check metadata methods
    assert agent.get_name() == "Test Agent"
    assert agent.get_description() == "A test agent"
    assert agent.get_capabilities() == ["test1", "test2"]
    assert agent.get_supported_domains() == ["domain1", "domain2"]
    assert agent.get_created_at() == now
    assert agent.get_updated_at() == now
    assert agent.get_custom_metadata() == custom_metadata


def test_agent_registration():
    """Test agent registration."""
    registry = InMemoryAgentRegistry()
    
    # Test data
    public_key = "0x1234567890abcdef"
    metadata = {
        "name": "Test Agent",
        "description": "A test agent",
        "capabilities": ["test1", "test2"],
        "domains": ["domain1", "domain2"],
        "custom_metadata": {"test": "value"}
    }
    signature = "0xsignature"  # Not actually validated in the mock implementation
    
    # Register the agent
    agent_id = registry.register_agent(public_key, metadata, signature)
    
    # Verify the agent was registered
    assert registry.verify_agent(agent_id)
    
    # Get the agent
    agent = registry.get_agent(agent_id)
    assert agent is not None
    assert agent.get_id() == agent_id
    assert agent.get_public_key() == public_key
    
    # Get the agent metadata
    agent_metadata = registry.get_agent_metadata(agent_id)
    assert agent_metadata is not None
    assert agent_metadata.get_name() == metadata["name"]
    assert agent_metadata.get_description() == metadata["description"]
    assert agent_metadata.get_capabilities() == metadata["capabilities"]
    assert agent_metadata.get_supported_domains() == metadata["domains"]
    assert agent_metadata.get_custom_metadata() == metadata["custom_metadata"]
    
    # Try to register the same agent again (should fail)
    with pytest.raises(DuplicateAgentError):
        registry.register_agent(public_key, metadata, signature)


def test_agent_update():
    """Test agent metadata update."""
    registry = InMemoryAgentRegistry()
    
    # Register an agent
    public_key = "0x1234567890abcdef"
    metadata = {
        "name": "Test Agent",
        "description": "A test agent",
        "capabilities": ["test1", "test2"],
        "domains": ["domain1", "domain2"],
        "custom_metadata": {"test": "value"}
    }
    signature = "0xsignature"
    agent_id = registry.register_agent(public_key, metadata, signature)
    
    # Update the agent metadata
    new_metadata = {
        "name": "Updated Agent",
        "description": "An updated agent",
        "capabilities": ["test1", "test2", "test3"],
        "domains": ["domain1", "domain2", "domain3"],
        "custom_metadata": {"test": "updated", "new": "value"}
    }
    registry.update_metadata(agent_id, new_metadata, signature)
    
    # Get the updated agent metadata
    agent_metadata = registry.get_agent_metadata(agent_id)
    assert agent_metadata.get_name() == new_metadata["name"]
    assert agent_metadata.get_description() == new_metadata["description"]
    assert agent_metadata.get_capabilities() == new_metadata["capabilities"]
    assert agent_metadata.get_supported_domains() == new_metadata["domains"]
    assert "test" in agent_metadata.get_custom_metadata()
    assert agent_metadata.get_custom_metadata()["test"] == "updated"
    assert "new" in agent_metadata.get_custom_metadata()
    assert agent_metadata.get_custom_metadata()["new"] == "value"


def test_agent_deactivation():
    """Test agent deactivation."""
    registry = InMemoryAgentRegistry()
    
    # Register an agent
    public_key = "0x1234567890abcdef"
    metadata = {
        "name": "Test Agent",
        "description": "A test agent",
        "capabilities": ["test"],
        "domains": ["test-domain"],
        "custom_metadata": {}
    }
    signature = "0xsignature"
    agent_id = registry.register_agent(public_key, metadata, signature)
    
    # Verify the agent is active
    assert registry.verify_agent(agent_id)
    
    # Deactivate the agent
    registry.deactivate_agent(agent_id, signature)
    
    # Verify the agent is no longer active
    assert not registry.verify_agent(agent_id)


def test_agent_query():
    """Test agent query functionality."""
    registry = InMemoryAgentRegistry()
    
    # Register multiple agents
    agents = [
        {
            "public_key": "0x1111",
            "metadata": {
                "name": "Agent 1",
                "description": "Agent 1 description",
                "capabilities": ["cap1", "cap2"],
                "domains": ["domain1", "domain2"],
                "custom_metadata": {}
            }
        },
        {
            "public_key": "0x2222",
            "metadata": {
                "name": "Agent 2",
                "description": "Agent 2 description",
                "capabilities": ["cap2", "cap3"],
                "domains": ["domain2", "domain3"],
                "custom_metadata": {}
            }
        },
        {
            "public_key": "0x3333",
            "metadata": {
                "name": "Agent 3",
                "description": "Agent 3 description",
                "capabilities": ["cap1", "cap3"],
                "domains": ["domain1", "domain3"],
                "custom_metadata": {}
            }
        }
    ]
    
    agent_ids = []
    for agent in agents:
        agent_id = registry.register_agent(agent["public_key"], agent["metadata"], "0xsignature")
        agent_ids.append(agent_id)
    
    # Test listing all agents
    all_agents = registry.list_agents()
    assert len(all_agents) == 3
    for agent_id in agent_ids:
        assert agent_id in all_agents
    
    # Test filtering by domain
    domain1_agents = registry.list_agents(domain="domain1")
    assert len(domain1_agents) == 2
    assert agent_ids[0] in domain1_agents
    assert agent_ids[2] in domain1_agents
    
    domain2_agents = registry.list_agents(domain="domain2")
    assert len(domain2_agents) == 2
    assert agent_ids[0] in domain2_agents
    assert agent_ids[1] in domain2_agents
    
    # Test filtering by capability
    cap1_agents = registry.list_agents(capability="cap1")
    assert len(cap1_agents) == 2
    assert agent_ids[0] in cap1_agents
    assert agent_ids[2] in cap1_agents
    
    cap2_agents = registry.list_agents(capability="cap2")
    assert len(cap2_agents) == 2
    assert agent_ids[0] in cap2_agents
    assert agent_ids[1] in cap2_agents
    
    # Test non-existent domain
    nonexistent_domain_agents = registry.list_agents(domain="nonexistent")
    assert len(nonexistent_domain_agents) == 0
    
    # Test non-existent capability
    nonexistent_cap_agents = registry.list_agents(capability="nonexistent")
    assert len(nonexistent_cap_agents) == 0


def test_agent_not_found():
    """Test handling of non-existent agents."""
    registry = InMemoryAgentRegistry()
    
    # Try to get a non-existent agent
    agent = registry.get_agent("nonexistent")
    assert agent is None
    
    # Try to get metadata for a non-existent agent
    metadata = registry.get_agent_metadata("nonexistent")
    assert metadata is None
    
    # Try to update a non-existent agent
    with pytest.raises(AgentNotFoundError):
        registry.update_metadata("nonexistent", {}, "0xsignature")
    
    # Try to deactivate a non-existent agent
    with pytest.raises(AgentNotFoundError):
        registry.deactivate_agent("nonexistent", "0xsignature")
    
    # Verify a non-existent agent
    assert not registry.verify_agent("nonexistent") 