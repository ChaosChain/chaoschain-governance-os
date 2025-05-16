#!/usr/bin/env python3
"""
Simple demo to test the imports
"""
import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.agent_registry import InMemoryAgentRegistry
from core.proof_of_agency import ActionType, InMemoryProofOfAgency
from core.secure_execution import MockSecureExecutionEnvironment

def main():
    # Create registry
    registry = InMemoryAgentRegistry()
    
    # Register an agent
    agent_id = registry.register_agent(
        "test@example.com",
        "Test Agent",
        {"role": "tester"}
    )
    
    print(f"Registered agent with ID: {agent_id}")
    
    # Create PoA
    poa = InMemoryProofOfAgency(registry)
    
    # Create SEE
    see = MockSecureExecutionEnvironment()
    
    print("Successfully imported and initialized all components!")

if __name__ == "__main__":
    main() 