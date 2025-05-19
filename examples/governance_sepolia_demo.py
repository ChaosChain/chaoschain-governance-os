#!/usr/bin/env python3
"""
Governance Analysis Sepolia Demo

This script demonstrates the governance analysis functionality
using real Sepolia testnet data with the option to anchor results on-chain.
"""

import os
import sys
import time
import json
import logging
import argparse
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Local imports
from agent.blockchain.proposal_iterator import ProposalIterator
from agent.blockchain.task_result import TaskResult
from agent.blockchain.context_fetcher import get_context_fetcher, USE_MOCK

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description='Governance Analysis Sepolia Demo')
    
    parser.add_argument(
        '--anchor-eth',
        action='store_true',
        default=True,
        help='Anchor analysis results on Ethereum (default: True)'
    )
    
    parser.add_argument(
        '--no-anchor-eth',
        action='store_false',
        dest='anchor_eth',
        help='Do not anchor analysis results on Ethereum'
    )
    
    parser.add_argument(
        '--network',
        type=str,
        default='sepolia',
        choices=['sepolia'],
        help='Ethereum testnet to use (default and only option: sepolia)'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='./results',
        help='Directory to save results (default: ./results)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    return parser.parse_args()

def create_mock_tx_hash() -> str:
    """Create a mock transaction hash for demonstration purposes."""
    timestamp = int(time.time())
    return f"0x{timestamp:x}{'0' * 56}"

def save_results(results: List[Dict[str, Any]], output_dir: str):
    """Save results to JSON files."""
    os.makedirs(output_dir, exist_ok=True)
    
    # Save results as a collection
    timestamp = int(time.time())
    collection_file = os.path.join(output_dir, f"proposal_analysis_{timestamp}.json")
    
    with open(collection_file, 'w') as f:
        json.dump({
            "timestamp": timestamp,
            "analysis_count": len(results),
            "results": results
        }, f, indent=2)
    
    logger.info(f"Saved combined results to {collection_file}")
    
    # Save individual markdown summaries
    for i, result in enumerate(results):
        if "markdown_summary" in result and result["markdown_summary"]:
            proposal_id = result.get("proposal_id", f"proposal_{i}")
            markdown_file = os.path.join(output_dir, f"analysis_{proposal_id}_{timestamp}.md")
            
            with open(markdown_file, 'w') as f:
                f.write(result["markdown_summary"])
            
            logger.info(f"Saved markdown summary to {markdown_file}")

def main():
    """Run the governance analysis demo on Sepolia testnet."""
    args = parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger.info("Starting Governance Analysis Sepolia Demo")
    logger.info(f"Network: {args.network}")
    logger.info(f"Anchor on Ethereum: {args.anchor_eth}")
    
    if USE_MOCK:
        logger.warning("MOCK MODE ENABLED - Using mock blockchain data")
        logger.warning("Set ETHEREUM_MOCK=false in your .env file to use real data")
    
    # Create proposal iterator
    iterator = ProposalIterator()
    
    # Fetch proposals
    logger.info("Fetching governance proposals from Sepolia testnet...")
    proposals = iterator.fetch_proposals()
    
    if not proposals:
        logger.warning("No active governance proposals found")
        return
    
    logger.info(f"Found {len(proposals)} active governance proposals")
    
    # Analyze proposals
    logger.info("Analyzing governance proposals...")
    analysis_results = []
    task_results = []
    
    for i, proposal in enumerate(proposals):
        logger.info(f"Analyzing proposal {i+1}/{len(proposals)}: {proposal.get('id', 'unknown')}")
        
        # Analyze the proposal
        result = iterator.analyze_proposal(proposal, use_markdown=True)
        analysis_results.append(result)
        
        # Create a task result
        if result.get("success", False):
            task_result = TaskResult.from_task_output(
                task_id=f"proposal-analysis-{proposal.get('id', 'unknown')}",
                task_name="ProposalAnalysis",
                output=result,
                markdown_summary=result.get("markdown_summary")
            )
            
            # Add a mock transaction hash if anchoring is enabled
            if args.anchor_eth:
                tx_hash = create_mock_tx_hash()
                task_result.set_receipt_tx_hash(tx_hash)
                
                # Print Etherscan URL
                etherscan_url = task_result.get_etherscan_url(args.network)
                logger.info(f"Etherscan URL: {etherscan_url}")
                
                # Add to the analysis result
                result["receipt_tx_hash"] = tx_hash
                result["etherscan_url"] = etherscan_url
            
            task_results.append(task_result)
    
    # Save results
    save_results(analysis_results, args.output_dir)
    
    # Print summary
    logger.info("\n" + "="*80)
    logger.info(f"Governance Analysis Summary:")
    logger.info(f"- Analyzed {len(proposals)} proposals")
    logger.info(f"- Generated {len(task_results)} analysis reports")
    
    for i, task_result in enumerate(task_results):
        proposal_id = task_result.get_output().get("proposal_id", f"unknown_{i}")
        risk_level = task_result.get_output().get("security_analysis", {}).get("risk_level", "unknown")
        mev_risk = task_result.get_output().get("mev_analysis", {}).get("risk_level", "unknown")
        
        logger.info(f"\nProposal {i+1}: {proposal_id}")
        logger.info(f"- Security Risk Level: {risk_level.upper()}")
        logger.info(f"- MEV Risk Level: {mev_risk.upper()}")
        
        if args.anchor_eth and task_result.get_receipt_tx_hash():
            logger.info(f"- Etherscan URL: {task_result.get_etherscan_url(args.network)}")
    
    logger.info("\nDone!")

if __name__ == "__main__":
    main() 