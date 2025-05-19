"""
Proposal Iterator

This module provides functionality to iterate through governance proposals
and execute analysis tasks on each one.
"""

import logging
import time
from typing import Dict, List, Any, Optional, Tuple

# Local imports
from agent.blockchain.context_fetcher import get_context_fetcher
from agent.task_registry import registry as task_registry
from agent.tasks import ProposalSanityScanner, MEVCostEstimator

logger = logging.getLogger(__name__)

class ProposalIterator:
    """
    Iterates through governance proposals and executes analysis tasks on each one.
    
    This class fetches pending proposals from the Sepolia testnet and runs
    security and MEV analysis on each proposal.
    """
    
    def __init__(self, secure_execution_env=None, proof_of_agency=None):
        """
        Initialize the proposal iterator.
        
        Args:
            secure_execution_env: Secure execution environment for tasks
            proof_of_agency: Proof of agency framework for recording actions
        """
        self.secure_env = secure_execution_env
        self.poa = proof_of_agency
        
    def fetch_proposals(self) -> List[Dict[str, Any]]:
        """
        Fetch pending governance proposals from the blockchain.
        
        Returns:
            List of governance proposals
        """
        logger.info("Fetching pending governance proposals")
        
        try:
            # Get the appropriate context fetcher
            fetcher = get_context_fetcher()
            
            # Fetch active governance proposals
            proposals = fetcher.get_active_governor_proposals()
            
            logger.info(f"Fetched {len(proposals)} active governance proposals")
            return proposals
        except Exception as e:
            logger.error(f"Error fetching governance proposals: {e}")
            return []
    
    def analyze_proposal(self, proposal: Dict[str, Any], use_markdown: bool = True) -> Dict[str, Any]:
        """
        Run analysis tasks on a single proposal.
        
        Args:
            proposal: Governance proposal to analyze
            use_markdown: Whether to include markdown summary in results
            
        Returns:
            Analysis results
        """
        if not proposal:
            logger.warning("Cannot analyze empty proposal")
            return {"success": False, "error": "Empty proposal"}
        
        logger.info(f"Analyzing proposal {proposal.get('id', 'unknown')}")
        
        results = {}
        
        # Create execution context for the tasks
        context = self._create_execution_context(proposal)
        
        # Run ProposalSanityScanner
        security_results = self._execute_task("ProposalSanityScanner", context)
        results["security_analysis"] = security_results
        
        # Run MEVCostEstimator
        mev_results = self._execute_task("MEVCostEstimator", context)
        results["mev_analysis"] = mev_results
        
        # Generate summary if needed
        if use_markdown and results.get("security_analysis", {}).get("success", False) and results.get("mev_analysis", {}).get("success", False):
            markdown_summary = self._generate_markdown_summary(proposal, security_results, mev_results)
            results["markdown_summary"] = markdown_summary
        
        # Overall success status
        results["success"] = (
            results.get("security_analysis", {}).get("success", False) and 
            results.get("mev_analysis", {}).get("success", False)
        )
        
        # Add proposal info to results
        results["proposal_id"] = proposal.get("id", "unknown")
        results["proposal_description"] = proposal.get("description", "No description")
        results["analysis_timestamp"] = int(time.time())
        
        return results
    
    def iterate_proposals(self, use_markdown: bool = True) -> List[Dict[str, Any]]:
        """
        Fetch and analyze all active governance proposals.
        
        Args:
            use_markdown: Whether to include markdown summary in results
            
        Returns:
            List of analysis results, one per proposal
        """
        logger.info("Starting governance proposal analysis")
        
        # Fetch proposals
        proposals = self.fetch_proposals()
        if not proposals:
            logger.info("No active governance proposals found")
            return []
        
        # Analyze each proposal
        results = []
        for proposal in proposals:
            proposal_results = self.analyze_proposal(proposal, use_markdown)
            results.append(proposal_results)
        
        logger.info(f"Completed analysis of {len(results)} proposals")
        return results
    
    def _execute_task(self, task_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a governance task.
        
        Args:
            task_name: Name of the task to execute
            context: Execution context
            
        Returns:
            Task execution results
        """
        logger.info(f"Executing task {task_name}")
        
        try:
            # Create task instance
            task_instance = task_registry.create_task(task_name)
            
            # Check if we have a secure execution environment
            if self.secure_env and self.poa:
                # Log action in Proof of Agency
                agent_id = "governance_analyst"
                action_id = self.poa.log_action(
                    agent_id=agent_id,
                    action_type=f"EXECUTE_TASK_{task_instance.task_type.upper()}",
                    description=f"Execute governance task: {task_name}",
                    data={
                        "task_id": task_instance.task_id,
                        "task_name": task_name
                    }
                )
                
                # Execute task in secure environment
                results = self.secure_env.execute(
                    function=task_instance.execute,
                    args=[context],
                    enclave_name="governance_task",
                    task_id=task_instance.task_id
                )
                
                # Record outcome in Proof of Agency
                self.poa.record_outcome(
                    action_id=action_id,
                    success=results.get("success", False),
                    results=results,
                    impact_score=0.7
                )
                
                return results
            else:
                # Execute directly if no secure environment
                return task_instance.execute(context)
                
        except Exception as e:
            logger.error(f"Error executing task {task_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "task_id": getattr(task_instance, "task_id", "unknown") if 'task_instance' in locals() else "unknown"
            }
    
    def _create_execution_context(self, proposal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create an execution context for the tasks.
        
        Args:
            proposal: Governance proposal
            
        Returns:
            Execution context
        """
        # Create basic context structure required by tasks
        return {
            "governance": {
                "proposal_data": proposal,
                "proposal_history": [],
                "governance_contract": {
                    "address": proposal.get("contract_address", "0x0000000000000000000000000000000000000000"),
                    "type": "governor"
                },
                "proposal_author": proposal.get("proposer", "0x0000000000000000000000000000000000000000")
            },
            "blockchain": {
                "contract_bytecode": {},
                "account_history": {},
                "recent_blocks": [],
                "gas_prices": [],
                "mempool_data": {"transaction_count": 0, "average_transaction_value": 0}
            },
            "context": {
                "protocol_parameters": {},
                "known_vulnerabilities": [],
                "timestamp": int(time.time()),
                "network": "sepolia"
            },
            "defi": {
                "trading_pairs": [],
                "pool_liquidity": {},
                "volume_data": {},
                "active_bots": []
            }
        }
    
    def _generate_markdown_summary(self, 
                                 proposal: Dict[str, Any], 
                                 security_results: Dict[str, Any], 
                                 mev_results: Dict[str, Any]) -> str:
        """
        Generate a markdown summary of the analysis results.
        
        Args:
            proposal: Governance proposal
            security_results: Results from ProposalSanityScanner
            mev_results: Results from MEVCostEstimator
            
        Returns:
            Markdown summary
        """
        # Format proposal details
        proposal_id = proposal.get("id", "unknown")
        contract_address = proposal.get("contract_address", "unknown")
        proposal_description = proposal.get("description", "No description")
        
        # Get risk assessments
        security_risk = security_results.get("risk_level", "unknown")
        mev_risk = mev_results.get("risk_level", "unknown")
        
        # Format issues and recommendations
        security_issues = security_results.get("issues", [])
        security_recommendations = security_results.get("recommendations", [])
        
        # Generate markdown
        markdown = f"""
# Governance Proposal Analysis

## Proposal Details
- **Proposal ID**: {proposal_id}
- **Contract**: {contract_address}
- **Description**: {proposal_description}

## Security Analysis
- **Risk Level**: {security_risk.upper()}
- **Risk Score**: {security_results.get("risk_score", 0):.2f}

### Issues Identified
"""
        
        if security_issues:
            for issue in security_issues[:3]:  # Show top 3 issues
                issue_type = issue.get("type", "unknown")
                severity = issue.get("severity", "unknown")
                description = issue.get("description", "No description")
                markdown += f"- **{issue_type}** ({severity}): {description}\n"
        else:
            markdown += "- No major security issues identified\n"
        
        markdown += """
### Recommendations
"""
        
        if security_recommendations:
            for rec in security_recommendations[:3]:  # Show top 3 recommendations
                markdown += f"- {rec}\n"
        else:
            markdown += "- No specific recommendations\n"
        
        # MEV analysis
        markdown += f"""
## MEV Impact Analysis
- **Risk Level**: {mev_risk.upper()}
- **Risk Score**: {mev_results.get("risk_score", 0):.2f}
- **Estimated MEV Cost**: {mev_results.get("estimated_total_mev_cost", 0):.2f} ETH
        
### MEV Vectors
"""
        
        mev_vectors = mev_results.get("mev_vectors", {})
        for vector_name, vector_data in mev_vectors.items():
            risk_score = vector_data.get("risk_score", 0)
            estimated_cost = vector_data.get("estimated_cost", 0)
            markdown += f"- **{vector_name}**: Risk {risk_score:.2f}, Est. Cost {estimated_cost:.2f} ETH\n"
        
        markdown += """
### Mitigations
"""
        
        mitigations = mev_results.get("mitigations", [])
        if mitigations:
            for mitigation in mitigations[:3]:  # Show top 3 mitigations
                markdown += f"- {mitigation}\n"
        else:
            markdown += "- No specific mitigations\n"
        
        markdown += f"""
## Analysis Timestamp
{time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime(int(time.time())))}
"""
        
        return markdown 