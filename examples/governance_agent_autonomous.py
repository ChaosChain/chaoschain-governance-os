#!/usr/bin/env python3
"""
Governance Agent Autonomous Demo

This script demonstrates the autonomous governance analyst agent that can
analyze blockchain data and execute governance tasks.
"""

import os
import sys
import logging
import json
import time
import argparse
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# Import mock components
from agent.mock_blockchain_client import MockBlockchainClient
from agent.mock_secure_execution import MockSecureExecutionEnvironment
from agent.mock_proof_of_agency import MockProofOfAgency
from agent.mock_agent_registry import MockAgentRegistry

# Import the agent
from agent.agents.governance_analyst_agent import GovernanceAnalystAgent, create_governance_analyst

def print_separator(title: str = None):
    """Print a separator line with an optional title."""
    width = 80
    if title:
        print(f"\n{' ' + title + ' ':=^{width}}\n")
    else:
        print("=" * width)

def print_json(data: Dict[str, Any]):
    """Print a dictionary as formatted JSON."""
    print(json.dumps(data, indent=2, default=str))

def run_agent_demo(
    task_type: Optional[str] = None,
    mock_failure: bool = False,
    use_langchain: bool = False,
    verbose: bool = False
):
    """
    Run the governance agent demonstration.
    
    Args:
        task_type: Optional specific task type to run
        mock_failure: Whether to simulate execution failures
        use_langchain: Whether to use LangChain
        verbose: Whether to enable verbose output
    """
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    print_separator("GOVERNANCE ANALYST AGENT DEMO")
    print("This demo showcases an autonomous governance analyst agent that")
    print("analyzes blockchain data and executes governance tasks.")
    print("\nThe agent will:")
    print("1. Collect blockchain data (blocks, gas prices, governance proposals)")
    print("2. Decide which governance task to execute based on the data")
    print("3. Execute the task in a secure environment")
    print("4. Record the action and outcome in the Proof of Agency system")
    print()
    
    # Step 1: Initialize system components
    print_separator("STEP 1: Initialize Components")
    
    print("Initializing mock blockchain client...")
    blockchain_client = MockBlockchainClient()
    
    print("Initializing mock agent registry...")
    agent_registry = MockAgentRegistry()
    
    print("Initializing mock Proof of Agency framework...")
    poa = MockProofOfAgency(agent_registry)
    
    print("Initializing mock secure execution environment...")
    secure_execution = MockSecureExecutionEnvironment(should_simulate_failure=mock_failure)
    
    # Step 2: Create the governance analyst agent
    print_separator("STEP 2: Create Governance Analyst Agent")
    
    agent = create_governance_analyst(
        blockchain_client=blockchain_client,
        secure_execution_env=secure_execution,
        proof_of_agency=poa
    )
    
    print(f"Available governance tasks: {agent.get_available_tasks()}")
    
    # Step 3: Execute the agent using the decide_and_run method
    print_separator("STEP 3: Execute Governance Analysis using decide_and_run()")
    
    # If no task_type is specified, let the agent decide
    if task_type:
        print(f"Using specified task: {task_type}")
    else:
        print("No task specified. Agent will decide which task to run based on blockchain data.")
    
    # Execute the agent - note we're using decide_and_run() instead of execute_governance_analysis()
    start_time = time.time()
    result = agent.decide_and_run(task_type=task_type)
    execution_time = time.time() - start_time
    
    print(f"Analysis completed in {execution_time:.2f} seconds")
    
    # Step 4: Show results
    print_separator("STEP 4: Results")
    
    print("Decision and execution result:")
    print_json(result)
    
    # Extract the selected task
    selected_task = result.get("selected_task", "Unknown")
    print(f"\nSelected task: {selected_task}")
    
    # Extract execution results
    execution_results = result.get("execution_results", {})
    if execution_results:
        print("\nExecution results:")
        print(f"Success: {execution_results.get('success', False)}")
        
        if "recommendations" in execution_results and execution_results["recommendations"]:
            print("\nRecommendations:")
            for rec in execution_results["recommendations"]:
                print(f"  - {rec}")
        
        if "issues" in execution_results and execution_results["issues"]:
            print("\nIssues detected:")
            for issue in execution_results["issues"]:
                print(f"  - {issue}")
        
        if "risk_level" in execution_results:
            print(f"\nRisk level: {execution_results['risk_level']}")
        
        if "estimated_total_mev_cost" in execution_results:
            print(f"\nEstimated MEV cost: {execution_results['estimated_total_mev_cost']}")
        
        if "error" in execution_results:
            print(f"\nError: {execution_results['error']}")
    
    # Step 5: Show Proof of Agency information
    print_separator("STEP 5: Proof of Agency Receipt")
    
    poa_action_id = result.get("poa_action_id")
    if poa_action_id:
        print(f"PoA Action ID: {poa_action_id}")
        
        # Get the full action chain for this specific action
        action_chain = poa.get_action_chain(poa_action_id)
        
        print("\nProof of Agency Receipt:")
        print_json(action_chain)
    else:
        print("No Proof of Agency action ID found in the result.")
    
    print_separator("DEMO COMPLETE")
    
    # Return overall success status
    is_successful = result.get("execution_results", {}).get("success", False)
    print(f"\nOverall execution success: {'SUCCESS' if is_successful else 'FAILURE'}")
    return is_successful

def main():
    """Run the main demo function."""
    parser = argparse.ArgumentParser(description='Governance Agent Autonomous Demo')
    parser.add_argument('--task', type=str, help='Specific task to run (GasParameterOptimizer, ProposalSanityScanner, MEVCostEstimator)')
    parser.add_argument('--mock-failure', action='store_true', help='Simulate execution failures')
    parser.add_argument('--use-langchain', action='store_true', help='Use LangChain for LLM integration')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    
    args = parser.parse_args()
    
    success = run_agent_demo(
        task_type=args.task,
        mock_failure=args.mock_failure,
        use_langchain=args.use_langchain,
        verbose=args.verbose
    )
    
    # Exit with appropriate status code for CI integration
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 