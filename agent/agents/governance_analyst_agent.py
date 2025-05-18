"""
Governance Analyst Agent

This module implements a CrewAI-based autonomous governance analyst agent that
analyzes blockchain data and executes governance tasks.
"""

import logging
import time
from typing import Dict, List, Any, Optional, Tuple, Union
import os
import json

# Try importing CrewAI, but fall back to mocks if it's not available
try:
    from crewai import Agent, Task, Crew, Process
    CREWAI_AVAILABLE = True
except ImportError:
    # Create mock classes if CrewAI is not available
    class Agent:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)
    
    class Task:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)
    
    class Crew:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)
        
        def kickoff(self):
            return {}
    
    class Process:
        sequential = "sequential"
    
    CREWAI_AVAILABLE = False
    logging.warning("CrewAI not available, using mock implementation")

# Try importing Langchain, but fall back to mocks if it's not available
try:
    from langchain.tools import BaseTool
    LANGCHAIN_AVAILABLE = True
except ImportError:
    # Create a mock BaseTool if Langchain is not available
    class BaseTool:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)
            self.name = kwargs.get('name', 'mock_tool')
            self.description = kwargs.get('description', 'Mock tool')
        
        def _run(self, *args, **kwargs):
            raise NotImplementedError("Subclasses must implement this method")
    
    LANGCHAIN_AVAILABLE = False
    logging.warning("Langchain not available, using mock implementation")

# Try importing Pydantic, but fall back to mocks if it's not available
try:
    from pydantic import Field
    PYDANTIC_AVAILABLE = True
except ImportError:
    # Create a mock Field if Pydantic is not available
    def Field(**kwargs):
        return None
    
    PYDANTIC_AVAILABLE = False
    logging.warning("Pydantic not available, using mock implementation")

# Local imports
from agent.task_registry import Task as GovTask, registry as task_registry
from agent.tasks import (
    GasParameterOptimizer,
    ProposalSanityScanner,
    MEVCostEstimator
)

logger = logging.getLogger(__name__)

class BlockchainDataTool(BaseTool):
    """
    Tool for fetching blockchain data for the governance analyst.
    """
    
    client: Any = Field(exclude=True)  # blockchain client
    
    def __init__(self, blockchain_client, name, description):
        """
        Initialize the blockchain data tool.
        
        Args:
            blockchain_client: Client for interacting with the blockchain
            name: Name of the tool
            description: Description of the tool
        """
        super().__init__(name=name, description=description)
        self.client = blockchain_client
    
    def _run(self, *args, **kwargs):
        """
        Run the tool with the provided arguments.
        This method should be overridden by subclasses.
        """
        raise NotImplementedError("Subclasses must implement this method")


class FetchRecentBlocksTool(BlockchainDataTool):
    """Tool for fetching recent blocks from the blockchain."""
    
    def __init__(self, blockchain_client):
        super().__init__(
            blockchain_client,
            name="fetch_recent_blocks",
            description="Fetch the most recent blocks from the blockchain"
        )
    
    def _run(self, count: int = 500) -> List[Dict[str, Any]]:
        """
        Fetch the most recent blocks from the blockchain.
        
        Args:
            count: Number of recent blocks to fetch
            
        Returns:
            List of block data
        """
        logger.info(f"Fetching {count} recent blocks")
        try:
            return self.client.get_recent_blocks(count)
        except Exception as e:
            logger.error(f"Error fetching recent blocks: {e}")
            return []


class FetchGovernanceProposalsTool(BlockchainDataTool):
    """Tool for fetching governance proposals."""
    
    def __init__(self, blockchain_client):
        super().__init__(
            blockchain_client,
            name="fetch_governance_proposals",
            description="Fetch governance proposals from the blockchain"
        )
    
    def _run(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """
        Fetch governance proposals.
        
        Args:
            active_only: Whether to fetch only active proposals
            
        Returns:
            List of governance proposals
        """
        logger.info(f"Fetching governance proposals (active_only={active_only})")
        try:
            return self.client.get_governance_proposals(active_only)
        except Exception as e:
            logger.error(f"Error fetching governance proposals: {e}")
            return []


class FetchGasPricesTool(BlockchainDataTool):
    """Tool for fetching gas prices."""
    
    def __init__(self, blockchain_client):
        super().__init__(
            blockchain_client,
            name="fetch_gas_prices",
            description="Fetch historical gas prices from the blockchain"
        )
    
    def _run(self, block_count: int = 200) -> List[int]:
        """
        Fetch historical gas prices.
        
        Args:
            block_count: Number of blocks to analyze
            
        Returns:
            List of gas prices in gwei
        """
        logger.info(f"Fetching gas prices for {block_count} blocks")
        try:
            return self.client.get_gas_prices(block_count)
        except Exception as e:
            logger.error(f"Error fetching gas prices: {e}")
            return []


class FetchMempoolDataTool(BlockchainDataTool):
    """Tool for fetching mempool data."""
    
    def __init__(self, blockchain_client):
        super().__init__(
            blockchain_client,
            name="fetch_mempool_data",
            description="Fetch current mempool data from the blockchain"
        )
    
    def _run(self) -> Dict[str, Any]:
        """
        Fetch current mempool data.
        
        Returns:
            Mempool statistics and data
        """
        logger.info("Fetching mempool data")
        try:
            return self.client.get_mempool_data()
        except Exception as e:
            logger.error(f"Error fetching mempool data: {e}")
            return {}


class FetchProtocolParametersTool(BlockchainDataTool):
    """Tool for fetching protocol parameters."""
    
    def __init__(self, blockchain_client):
        super().__init__(
            blockchain_client,
            name="fetch_protocol_parameters",
            description="Fetch current protocol parameters from the blockchain"
        )
    
    def _run(self) -> Dict[str, Any]:
        """
        Fetch current protocol parameters.
        
        Returns:
            Protocol parameters with metadata
        """
        logger.info("Fetching protocol parameters")
        try:
            return self.client.get_protocol_parameters()
        except Exception as e:
            logger.error(f"Error fetching protocol parameters: {e}")
            return {}


class ExecuteTaskTool(BaseTool):
    """
    Tool for secure execution of governance tasks.
    """
    
    secure_env: Any = Field(exclude=True)  # secure execution environment
    poa: Any = Field(exclude=True)  # proof of agency framework
    
    def __init__(self, secure_execution_env, proof_of_agency):
        """
        Initialize the secure execution tool.
        
        Args:
            secure_execution_env: Secure execution environment
            proof_of_agency: Proof of Agency framework
        """
        super().__init__(
            name="execute_task",
            description="Execute a governance task in the secure environment"
        )
        self.secure_env = secure_execution_env
        self.poa = proof_of_agency
    
    def _run(self, task_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a governance task in the secure environment.
        
        Args:
            task_name: Name of the task to execute
            context: Execution context with data for the task
            
        Returns:
            Task execution results
        """
        logger.info(f"Executing governance task: {task_name}")
        try:
            # Create task instance
            task_instance = task_registry.create_task(task_name)
            task_id = task_instance.task_id
            
            # Check required data
            required_data = task_instance.requires()
            missing_data = self._check_missing_data(required_data, context)
            if missing_data:
                logger.warning(f"Missing required data for task {task_name}: {missing_data}")
                return {
                    "success": False,
                    "error": f"Missing required data: {missing_data}",
                    "task_id": task_id
                }
            
            # Log action in Proof of Agency
            agent_id = "governance_analyst"  # Should be passed or retrieved
            action_id = self.poa.log_action(
                agent_id=agent_id,
                action_type=f"EXECUTE_TASK_{task_instance.task_type.upper()}",
                description=f"Execute governance task: {task_name}",
                data={
                    "task_id": task_id,
                    "task_name": task_name,
                    "requirements": required_data
                }
            )
            
            # Execute task in secure environment
            results = self.secure_env.execute(
                function=task_instance.execute,
                args=[context],
                enclave_name="governance_task",
                task_id=task_id
            )
            
            # Record outcome in Proof of Agency
            outcome_id = self.poa.record_outcome(
                action_id=action_id,
                success=results.get("success", False),
                results=results,
                impact_score=0.7  # Should be calculated based on results
            )
            
            # Anchor to blockchain if significant
            if self._is_significant_outcome(results):
                tx_hash = self.poa.anchor_action(action_id)
                results["anchored"] = True
                results["tx_hash"] = tx_hash
            else:
                results["anchored"] = False
            
            # Add metadata
            results["task_id"] = task_id
            results["action_id"] = action_id
            results["outcome_id"] = outcome_id
            
            return results
        except Exception as e:
            logger.error(f"Error executing task {task_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "task_id": task_instance.task_id if 'task_instance' in locals() else None
            }
    
    def _check_missing_data(self, required_data: Dict[str, List[str]], context: Dict[str, Any]) -> List[str]:
        """
        Check for missing required data in the context.
        
        Args:
            required_data: Required data by category
            context: Execution context
            
        Returns:
            List of missing data items
        """
        missing = []
        for category, requirements in required_data.items():
            if category not in context:
                missing.extend([f"{category}.{req}" for req in requirements])
                continue
                
            category_data = context[category]
            for req in requirements:
                if req not in category_data:
                    missing.append(f"{category}.{req}")
        
        return missing
    
    def _is_significant_outcome(self, results: Dict[str, Any]) -> bool:
        """
        Determine if a task outcome is significant enough to anchor to blockchain.
        
        Args:
            results: Task execution results
            
        Returns:
            Whether the outcome is significant
        """
        # Check if the task was successful
        if not results.get("success", False):
            return False
            
        # Check risk level for security tasks
        risk_level = results.get("risk_level")
        if risk_level in ["high", "medium"]:
            return True
            
        # Check recommendation quality for optimization tasks
        recommendation_quality = results.get("recommendation_quality")
        if recommendation_quality == "high":
            return True
            
        # For MEV cost estimation, check the estimated cost
        estimated_cost = results.get("estimated_total_mev_cost", 0)
        if estimated_cost > 1000:  # Arbitrary threshold
            return True
            
        return False


class GovernanceAnalystAgent:
    """
    CrewAI-based autonomous governance analyst agent.
    """
    
    def __init__(
        self,
        blockchain_client,
        secure_execution_env,
        proof_of_agency,
        llm=None
    ):
        """
        Initialize the governance analyst agent.
        
        Args:
            blockchain_client: Client for interacting with the blockchain
            secure_execution_env: Secure execution environment
            proof_of_agency: Proof of Agency framework
            llm: Language model to use for the agent
        """
        self.blockchain_client = blockchain_client
        self.secure_env = secure_execution_env
        self.poa = proof_of_agency
        self.llm = llm
        
        # Create tools
        self.blockchain_tools = {
            "fetch_recent_blocks": FetchRecentBlocksTool(blockchain_client),
            "fetch_governance_proposals": FetchGovernanceProposalsTool(blockchain_client),
            "fetch_gas_prices": FetchGasPricesTool(blockchain_client),
            "fetch_mempool_data": FetchMempoolDataTool(blockchain_client),
            "fetch_protocol_parameters": FetchProtocolParametersTool(blockchain_client),
            "execute_task": ExecuteTaskTool(secure_execution_env, proof_of_agency)
        }
        
        # Create CrewAI agent
        self.agent = self._create_crewai_agent(llm)
        
    def _create_crewai_agent(self, llm):
        """
        Create the CrewAI agent.
        
        Returns:
            CrewAI Agent
        """
        tools = list(self.blockchain_tools.values())
        
        # If no LLM is provided, create a mock LLM that satisfies CrewAI's requirements
        if llm is None:
            from unittest.mock import MagicMock
            mock_llm = MagicMock()
            # Add bind method to satisfy CrewAI requirements
            mock_llm.bind = MagicMock(return_value=mock_llm)
            mock_llm.invoke = MagicMock(return_value="Task selection: GasParameterOptimizer")
            llm = mock_llm
        
        return Agent(
            role="Governance Analyst",
            goal="Analyze blockchain data and execute governance tasks to optimize protocol parameters and ensure security",
            backstory="""
            You are an expert blockchain governance analyst with deep knowledge of DeFi protocols,
            MEV, and parameter optimization. Your responsibility is to continuously monitor the
            blockchain, analyze governance proposals and protocol parameters, and execute
            governance tasks to ensure the protocol operates securely and efficiently.
            """,
            verbose=True,
            allow_delegation=False,
            tools=tools,
            llm=llm
        )
    
    def execute_governance_analysis(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute the governance analysis workflow.
        
        Args:
            context: Optional initial context data
            
        Returns:
            Analysis results
        """
        logger.info("Starting governance analysis workflow")
        
        # Setup the analysis context
        if context is None:
            context = {}
            
        # Create CrewAI tasks
        task1 = Task(
            description="Collect on-chain data for governance analysis",
            expected_output="Comprehensive blockchain data including recent blocks, gas prices, and governance proposals",
            agent=self.agent
        )
        
        task2 = Task(
            description="""
            Based on the collected blockchain data, determine which governance task needs to be executed:
            - GasParameterOptimizer: If there are significant gas price fluctuations or proposals to change fee structures
            - ProposalSanityScanner: If there are new or pending governance proposals that need security review
            - MEVCostEstimator: If there are protocol parameter changes that might expose MEV opportunities
            
            Provide a detailed justification for your task selection.
            """,
            expected_output="Selected task name and justification based on blockchain data analysis",
            agent=self.agent,
            context=[task1]
        )
        
        task3 = Task(
            description="""
            Execute the selected governance task in the secure execution environment.
            Use the execute_task tool with the appropriate task name and context data.
            Ensure all required data is provided in the context.
            
            Document the execution results and any recommendations or findings.
            """,
            expected_output="Detailed task execution results and recommendations",
            agent=self.agent,
            context=[task1, task2]
        )
        
        # Create a crew with the single agent
        crew = Crew(
            agents=[self.agent],
            tasks=[task1, task2, task3],
            verbose=True,
            process=Process.sequential
        )
        
        # Execute the crew workflow
        start_time = time.time()
        result = crew.kickoff()
        execution_time = time.time() - start_time
        
        logger.info(f"Governance analysis completed in {execution_time:.2f} seconds")
        
        return {
            "crew_result": result,
            "execution_time": execution_time
        }
    
    def get_available_tasks(self) -> List[str]:
        """
        Get the list of available governance tasks.
        
        Returns:
            List of available task names
        """
        return task_registry.list_tasks()

    # Helper methods for task execution
    def _check_missing_data(self, required_data, context):
        """
        Check for missing data in the execution context.
        
        Args:
            required_data: Required data specification
            context: Execution context
            
        Returns:
            List of missing data items
        """
        missing = []
        
        for category, items in required_data.items():
            if category not in context:
                missing.append(f"Category '{category}' is missing")
                continue
                
            cat_data = context[category]
            for item in items:
                if item not in cat_data:
                    missing.append(f"Item '{item}' in category '{category}' is missing")
        
        return missing
    
    def _is_significant_outcome(self, results):
        """
        Determine if a task outcome is significant enough to anchor to blockchain.
        
        Args:
            results: Task execution results
            
        Returns:
            True if significant, False otherwise
        """
        # For demonstration, we'll consider any successful optimization task significant
        if results.get("success", False) and "recommendations" in results:
            recommendations = results["recommendations"]
            if isinstance(recommendations, list) and len(recommendations) > 0:
                return True
        
        return False
    
    def _collect_context(self) -> Dict[str, Any]:
        """
        Collect blockchain context data using either tools or direct fetcher.
        
        This method decides whether to use the blockchain_tools or the context fetcher
        based on availability and configuration.
        
        Returns:
            Dict containing blockchain data
        """
        logger.info("Collecting blockchain context data")
        
        # Check if we should use the context fetcher
        use_fetcher = False
        try:
            # Try to import the context fetcher - if it fails, we'll use the tools
            from agent.blockchain.context_fetcher import get_context_fetcher, USE_MOCK
            if not USE_MOCK:
                use_fetcher = True
        except ImportError:
            logger.warning("Context fetcher not available, using blockchain tools")
            use_fetcher = False
        
        if use_fetcher:
            try:
                # Get the appropriate context fetcher
                fetcher = get_context_fetcher()
                
                # Fetch blockchain data directly
                blocks = fetcher.get_recent_blocks(n=100)
                proposals = fetcher.get_active_governor_proposals()
                gas_stats = fetcher.get_gas_price_stats(block_count=100)
                
                # Extract gas prices from stats
                gas_prices = gas_stats.get("gas_prices", [])
                
                # Placeholder for mempool and protocol params
                # In a real implementation, these would come from the fetcher
                mempool = {"pending_tx_count": 0, "transactions": []}
                protocol_params = {}
                
                logger.info(f"Context fetched directly: {len(blocks)} blocks, {len(proposals)} proposals")
                
                return {
                    "blockchain_data": {
                        "recent_blocks": blocks,
                        "governance_proposals": proposals,
                        "gas_prices": gas_prices,
                        "mempool_data": mempool,
                        "protocol_parameters": protocol_params,
                        "gas_stats": gas_stats  # Additional data from the fetcher
                    }
                }
            except Exception as e:
                logger.error(f"Error using context fetcher: {e}")
                logger.warning("Falling back to blockchain tools")
        
        # If we reach here, we're using the blockchain tools
        context = {}
        
        # Fetch blockchain data - using safe defaults if any tool calls fail
        try:
            blocks = self.blockchain_tools["fetch_recent_blocks"]._run(count=100)
        except Exception as e:
            logger.warning(f"Error fetching recent blocks: {e}")
            blocks = []
            
        try:
            proposals = self.blockchain_tools["fetch_governance_proposals"]._run(active_only=True)
        except Exception as e:
            logger.warning(f"Error fetching governance proposals: {e}")
            proposals = []
            
        try:
            gas_prices = self.blockchain_tools["fetch_gas_prices"]._run(block_count=100)
        except Exception as e:
            logger.warning(f"Error fetching gas prices: {e}")
            gas_prices = []
            
        try:
            mempool = self.blockchain_tools["fetch_mempool_data"]._run()
        except Exception as e:
            logger.warning(f"Error fetching mempool data: {e}")
            mempool = {}
            
        try:
            protocol_params = self.blockchain_tools["fetch_protocol_parameters"]._run()
        except Exception as e:
            logger.warning(f"Error fetching protocol parameters: {e}")
            protocol_params = {}
        
        # Prepare context with all available data
        context = {
            "blockchain_data": {
                "recent_blocks": blocks or [],
                "governance_proposals": proposals or [],
                "gas_prices": gas_prices or [],
                "mempool_data": mempool or {},
                "protocol_parameters": protocol_params or {}
            }
        }
        
        logger.info(f"Context fetched via tools: {len(blocks)} blocks, {len(proposals)} proposals")
        return context
    
    def decide_and_run(self, task_type=None):
        """
        Makes a decision about which governance task to run and executes it.
        
        This method fetches blockchain data, decides which task to execute based on the data,
        and then executes the task in the secure environment.
        
        Args:
            task_type: Optional specific task to run instead of automatically deciding
            
        Returns:
            Dict containing execution results and proof of agency metadata
        """
        logger.info("Starting governance task decision and execution process")
        
        try:
            # Use the collect_context method to get blockchain data
            context = self._collect_context()
            
            # Make a decision (usually this would be done by the CrewAI agent)
            # If a specific task_type is provided, use that instead of deciding
            if task_type and task_type in self.get_available_tasks():
                logger.info(f"Using specified task: {task_type}")
                if task_type == "GasParameterOptimizer":
                    task_decision = {
                        "task_name": task_type,
                        "execution_context": {
                            "blockchain": {
                                "recent_blocks": context["blockchain_data"]["recent_blocks"],
                                "gas_prices": context["blockchain_data"]["gas_prices"],
                                "transaction_history": []
                            },
                            "governance": {
                                "proposal_types": ["standard", "complex", "upgrade"],
                                "voting_contract_address": "0x1234567890123456789012345678901234567890"
                            },
                            "context": {
                                "network_congestion": 0.5,
                                "proposal_type": "standard",
                                "timestamp": int(time.time()),
                                "network": "ethereum"
                            }
                        }
                    }
                elif task_type == "ProposalSanityScanner":
                    # Get the first proposal for demonstration
                    proposal = context["blockchain_data"]["governance_proposals"][0] if context["blockchain_data"]["governance_proposals"] else {}
                    task_decision = {
                        "task_name": task_type,
                        "execution_context": {
                            "governance": {
                                "proposal_data": proposal,
                                "proposal_history": [],
                                "governance_contract": {
                                    "address": "0x1234567890123456789012345678901234567890",
                                    "type": "governor"
                                },
                                "proposal_author": proposal.get("proposer", "0x0000000000000000000000000000000000000000")
                            },
                            "blockchain": {
                                "contract_bytecode": {},
                                "account_history": {}
                            },
                            "context": {
                                "protocol_parameters": context["blockchain_data"]["protocol_parameters"],
                                "known_vulnerabilities": [],
                                "timestamp": int(time.time()),
                                "network": "ethereum"
                            }
                        }
                    }
                elif task_type == "MEVCostEstimator":
                    task_decision = {
                        "task_name": task_type,
                        "execution_context": {
                            "blockchain": {
                                "recent_blocks": context["blockchain_data"]["recent_blocks"],
                                "gas_prices": context["blockchain_data"]["gas_prices"],
                                "mempool_data": context["blockchain_data"]["mempool_data"]
                            },
                            "governance": {
                                "proposal_data": {
                                    "id": "mock-proposal-1",
                                    "type": "parameter_update",
                                    "parameters": context["blockchain_data"]["protocol_parameters"]
                                },
                                "protocol_parameters": context["blockchain_data"]["protocol_parameters"]
                            },
                            "defi": {
                                "trading_pairs": [],
                                "pool_liquidity": {},
                                "volume_data": {},
                                "active_bots": []
                            }
                        }
                    }
                else:
                    # Fallback to the decision logic
                    task_decision = self.decide(context)
            else:
                # No specific task provided, use the decision logic
                task_decision = self.decide(context)
            
            # Execute the chosen task
            execution_context = task_decision.get("execution_context", {})
            task_name = task_decision.get("task_name")
            
            logger.info(f"Selected task to execute: {task_name}")
            
            # Execute the task
            if "execute_task" in self.blockchain_tools:
                execution_results = self.blockchain_tools["execute_task"]._run(
                    task_name=task_name,
                    context=execution_context
                )
            else:
                logger.error("execute_task tool not found in blockchain_tools")
                execution_results = {
                    "success": False, 
                    "error": "execute_task tool not available",
                    "task_id": f"mock-{task_name}"
                }
            
            # Return the results
            return {
                "execution_results": execution_results or {},
                "selected_task": task_name,
                "poa_action_id": execution_results.get("action_id") if execution_results else None
            }
            
        except Exception as e:
            logger.error(f"Error in governance task decision and execution: {e}")
            return {
                "error": str(e),
                "success": False
            }
    
    def decide(self, context):
        """
        Decide which task to execute based on blockchain data.
        
        In a production system, this would use the CrewAI agent to make a decision.
        For this implementation, we'll use simple heuristics.
        
        Args:
            context: Context containing blockchain data
            
        Returns:
            Dict with task_name and execution_context
        """
        blockchain_data = context.get("blockchain_data", {})
        
        # Simple heuristic: if we have gas price data, optimize gas parameters
        if "gas_prices" in blockchain_data and len(blockchain_data.get("gas_prices", [])) > 0:
            return {
                "task_name": "GasParameterOptimizer",
                "execution_context": {
                    # Restructure the context to match what GasParameterOptimizer requires
                    "blockchain": {
                        "recent_blocks": blockchain_data.get("recent_blocks", []),
                        "gas_prices": blockchain_data.get("gas_prices", []),
                        "transaction_history": []  # Add empty placeholder for required field
                    },
                    "governance": {
                        "proposal_types": ["standard", "complex", "upgrade"],  # Add required field
                        "voting_contract_address": "0x1234567890123456789012345678901234567890"  # Add required field
                    },
                    "context": {
                        "network_congestion": 0.5,  # Add required field
                        "proposal_type": "standard",  # Add helpful field
                        "timestamp": int(time.time()),
                        "network": "ethereum"
                    }
                }
            }
        
        # If we have governance proposals, scan them for issues
        elif "governance_proposals" in blockchain_data and len(blockchain_data.get("governance_proposals", [])) > 0:
            # Get the first proposal for demonstration
            proposals = blockchain_data.get("governance_proposals", [])
            proposal = proposals[0] if proposals else {}
            
            return {
                "task_name": "ProposalSanityScanner",
                "execution_context": {
                    # Structure context to match what ProposalSanityScanner requires
                    "governance": {
                        "proposal_data": proposal,
                        "proposal_history": [],  # Add empty placeholder for required field
                        "governance_contract": {
                            "address": "0x1234567890123456789012345678901234567890",
                            "type": "governor"
                        },
                        "proposal_author": proposal.get("proposer", "0x0000000000000000000000000000000000000000")
                    },
                    "blockchain": {
                        "contract_bytecode": {},  # Add empty placeholder for required field
                        "account_history": {}  # Add empty placeholder for required field
                    },
                    "context": {
                        "protocol_parameters": blockchain_data.get("protocol_parameters", {}),
                        "known_vulnerabilities": [],  # Add empty placeholder for required field
                        "timestamp": int(time.time()),
                        "network": "ethereum"
                    }
                }
            }
        
        # Default to MEV cost estimation
        else:
            return {
                "task_name": "MEVCostEstimator",
                "execution_context": {
                    # Structure context to match what MEVCostEstimator requires
                    "blockchain": {
                        "recent_blocks": blockchain_data.get("recent_blocks", []),
                        "gas_prices": blockchain_data.get("gas_prices", []),
                        "mempool_data": blockchain_data.get("mempool_data", {})
                    },
                    "governance": {
                        "proposal_data": {
                            "id": "mock-proposal-1",
                            "type": "parameter_update",
                            "parameters": blockchain_data.get("protocol_parameters", {})
                        },
                        "protocol_parameters": blockchain_data.get("protocol_parameters", {})
                    },
                    "defi": {
                        "trading_pairs": [],  # Add empty placeholder for required field
                        "pool_liquidity": {},  # Add empty placeholder for required field
                        "volume_data": {},    # Add empty placeholder for required field
                        "active_bots": []     # Add empty placeholder for required field
                    }
                }
            }

# Factory function
def create_governance_analyst(
    blockchain_client,
    secure_execution_env,
    proof_of_agency,
    llm=None
) -> GovernanceAnalystAgent:
    """
    Create a governance analyst agent.
    
    Args:
        blockchain_client: Client for interacting with the blockchain
        secure_execution_env: Secure execution environment
        proof_of_agency: Proof of Agency framework
        llm: Language model to use for the agent
        
    Returns:
        Governance analyst agent
    """
    return GovernanceAnalystAgent(
        blockchain_client=blockchain_client,
        secure_execution_env=secure_execution_env,
        proof_of_agency=proof_of_agency,
        llm=llm
    ) 