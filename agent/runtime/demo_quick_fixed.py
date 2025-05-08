#!/usr/bin/env python
"""
ChaosChain Quick Governance Demo

This script runs a simplified demo of the ChaosChain governance system
using a deterministic dataset without external API dependencies.
"""

import os
import sys
import json
import argparse
import logging
import dotenv
from typing import Dict, Any

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from agent.agents.quick_demo_fixed import QuickDemo

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("chaoschain.demo_quick")

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="ChaosChain Quick Governance Demo")
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
    return parser.parse_args()

def main():
    """Run the quick governance demo."""
    # Load environment variables from .env file
    dotenv.load_dotenv()
    
    # Parse command line arguments
    args = parse_args()
    
    logger.info("Starting ChaosChain Quick Governance Demo")
    
    # Create and run the governance demo with fixed implementation
    demo = QuickDemo(llm=args.model, verbose=args.verbose)
    
    try:
        logger.info("Running governance workflow...")
        results = demo.run()
        
        # Print results
        logger.info("Governance workflow completed:")
        logger.info("Analysis Summary:")
        print(results["analysis"])
        logger.info("\nProposal Summary:")
        print(results["proposal"])
        
        # Save results to file if requested
        if args.output:
            with open(args.output, "w") as f:
                json.dump(results, f, indent=2)
            logger.info(f"Results saved to {args.output}")
            
        logger.info("Demo completed successfully")
        
    except Exception as e:
        logger.error(f"Error running governance workflow: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 