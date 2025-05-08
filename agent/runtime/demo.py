#!/usr/bin/env python
"""
ChaosChain Governance Demo

This script demonstrates the core functionality of the ChaosChain governance system
by running a governance agents team to analyze blockchain metrics and generate proposals.
"""

import os
import sys
import json
import argparse
import logging
import asyncio
import dotenv
from typing import Dict, Any, Optional
from contextlib import contextmanager

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from agent.agents.governance_agents import GovernanceAgents

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("chaoschain.demo")

# Initialize streaming if needed
ENABLE_STREAM = os.environ.get("ENABLE_STREAM", "0") == "1"
stream_queue = None

if ENABLE_STREAM:
    try:
        # Only import these when streaming is enabled
        from api.rest.routers.stream import add_log_message
        
        # Create a custom handler for streaming logs
        class AgentStreamHandler(logging.Handler):
            def emit(self, record):
                try:
                    # Extract agent info if available
                    agent_name = getattr(record, "agent", "System")
                    msg = self.format(record)
                    
                    # Use asyncio to send to queue
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        asyncio.create_task(
                            add_log_message(agent_name, record.levelname.lower(), msg)
                        )
                except Exception:
                    self.handleError(record)
        
        # Add the handler to the root logger
        stream_handler = AgentStreamHandler()
        stream_handler.setLevel(logging.INFO)
        logging.getLogger().addHandler(stream_handler)
        
        logger.info("Streaming logs enabled")
    except ImportError:
        logger.warning("Could not import streaming modules. Streaming disabled.")
        ENABLE_STREAM = False

@contextmanager
def agent_logger(agent_name: str):
    """Context manager to add agent name to logs."""
    old_factory = logging.getLogRecordFactory()
    
    def record_factory(*args, **kwargs):
        record = old_factory(*args, **kwargs)
        record.agent = agent_name
        return record
    
    logging.setLogRecordFactory(record_factory)
    try:
        yield
    finally:
        logging.setLogRecordFactory(old_factory)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="ChaosChain Governance Demo")
    parser.add_argument(
        "--rpc", 
        type=str, 
        help="Ethereum RPC URL", 
        default=os.environ.get("ETHEREUM_RPC_URL", "")
    )
    parser.add_argument(
        "--verbose", 
        action="store_true", 
        help="Enable verbose output"
    )
    parser.add_argument(
        "--model", 
        type=str, 
        help="LLM model to use", 
        default=os.environ.get("OPENAI_MODEL_NAME", "gpt-4")
    )
    parser.add_argument(
        "--output", 
        type=str, 
        help="Output file for results (JSON)", 
        default=""
    )
    parser.add_argument(
        "--stream",
        action="store_true",
        help="Enable streaming logs to the API"
    )
    return parser.parse_args()

def setup_environment(args):
    """Set up environment variables from arguments."""
    if args.rpc:
        os.environ["ETHEREUM_RPC_URL"] = args.rpc
    
    if args.stream:
        os.environ["ENABLE_STREAM"] = "1"
    
    # Validate essential environment variables
    if not os.environ.get("ETHEREUM_RPC_URL"):
        logger.error("ETHEREUM_RPC_URL environment variable not set")
        sys.exit(1)

def main():
    """Run the governance demo."""
    # Load environment variables from .env file
    dotenv.load_dotenv()
    
    # Parse command line arguments
    args = parse_args()
    
    # Set up environment
    setup_environment(args)
    
    with agent_logger("System"):
        logger.info("Starting ChaosChain Governance Demo")
        logger.info(f"Using RPC URL: {os.environ.get('ETHEREUM_RPC_URL')}")
    
    # Create and run the governance agents
    agents = GovernanceAgents(llm=args.model, verbose=args.verbose)
    
    try:
        with agent_logger("System"):
            logger.info("Running governance workflow...")
        
        results = agents.run()
        
        # Print results
        with agent_logger("System"):
            logger.info("Governance workflow completed:")
            logger.info("Analysis Summary:")
        print(results["analysis"])
        
        with agent_logger("System"):
            logger.info("\nProposal Summary:")
        print(results["proposal"])
        
        # Save results to file if requested
        if args.output:
            with open(args.output, "w") as f:
                json.dump(results, f, indent=2)
            
            with agent_logger("System"):
                logger.info(f"Results saved to {args.output}")
        
        with agent_logger("System"):
            logger.info("Demo completed successfully")
        
    except Exception as e:
        with agent_logger("System"):
            logger.error(f"Error running governance workflow: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 