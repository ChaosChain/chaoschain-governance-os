"""
Governance Agents

This module implements a CrewAI team for blockchain governance,
combining researcher and developer agents to generate parameter optimization proposals.
"""

import os
import logging
from typing import Dict, Any, Optional
from crewai import Crew, Task, Agent
from contextlib import contextmanager

from agent.agents.researcher.gas_metrics_researcher import GasMetricsResearcher
from agent.agents.developer.parameter_optimizer import ParameterOptimizer

# Get logger
logger = logging.getLogger("chaoschain.governance")

@contextmanager
def agent_logger(agent_name: str):
    """Context manager to add agent name to logs."""
    # Only use this if it's not already defined elsewhere
    # Check if the context manager exists in the runtime module
    try:
        from agent.runtime.demo import agent_logger as runtime_agent_logger
        with runtime_agent_logger(agent_name):
            yield
    except ImportError:
        # Fallback to local implementation
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


class GovernanceAgents:
    """
    A CrewAI team for blockchain governance, combining researcher and developer agents
    to generate parameter optimization proposals.
    """
    
    def __init__(self, llm=None, verbose=False):
        """
        Initialize the governance agents.
        
        Args:
            llm: Language model to use (defaults to CrewAI default)
            verbose: Enable verbose logging
        """
        self.verbose = verbose
        self.llm = llm
        
        # Initialize agents with custom callbacks for logging
        with agent_logger("Gas Metrics Researcher"):
            logger.info("Initializing Gas Metrics Researcher agent")
            self.researcher = GasMetricsResearcher(llm=llm, verbose=verbose).get_agent()
        
        with agent_logger("Parameter Optimizer"):
            logger.info("Initializing Parameter Optimizer agent")
            self.developer = ParameterOptimizer(llm=llm, verbose=verbose).get_agent()
        
        # Create the crew
        with agent_logger("System"):
            logger.info("Creating governance crew with researcher and optimizer agents")
            self.crew = Crew(
                agents=[self.researcher, self.developer],
                tasks=self._create_tasks(),
                verbose=verbose,
                process_callbacks=[self._log_process_callback]
            )
    
    def _log_process_callback(self, data: Dict[str, Any]) -> None:
        """Callback to log CrewAI process events."""
        event_type = data.get("event_type", "unknown")
        if event_type == "agent_started":
            agent_name = data.get("agent", {}).get("name", "Unknown Agent")
            task_desc = data.get("task", {}).get("description", "")
            
            with agent_logger(agent_name):
                logger.info(f"Starting task: {task_desc[:50]}...")
        
        elif event_type == "agent_finished":
            agent_name = data.get("agent", {}).get("name", "Unknown Agent")
            output = data.get("output", "")
            
            with agent_logger(agent_name):
                logger.info(f"Completed task. Output length: {len(output)} chars")
        
        elif event_type == "task_started":
            task_id = data.get("task", {}).get("id", "unknown")
            
            with agent_logger("System"):
                logger.info(f"Task started: {task_id}")
        
        elif event_type == "task_finished":
            task_id = data.get("task", {}).get("id", "unknown")
            
            with agent_logger("System"):
                logger.info(f"Task completed: {task_id}")
    
    def _create_tasks(self) -> list:
        """
        Create the tasks for the governance agents.
        
        Returns:
            List of CrewAI tasks
        """
        with agent_logger("System"):
            logger.info("Creating research task for gas metrics analysis")
            
        research_task = Task(
            description="""
            Analyze Ethereum gas metrics to identify potential optimization opportunities.
            
            Use the analyze_gas_metrics tool to retrieve gas metrics data and provide analysis.
            """,
            agent=self.researcher,
            expected_output="A detailed analysis of gas metrics with identified optimization opportunities"
        )
        
        with agent_logger("System"):
            logger.info("Creating proposal task for parameter optimization")
            
        proposal_task = Task(
            description="""
            Generate a parameter optimization proposal based on the researcher's findings.
            
            Review the researcher's analysis and use the create_proposal tool to generate 
            an optimized parameter proposal.
            """,
            agent=self.developer,
            expected_output="A detailed parameter optimization proposal with simulation results",
            context=[research_task]
        )
        
        return [research_task, proposal_task]
    
    def run(self) -> Dict[str, Any]:
        """
        Run the governance agents workflow.
        
        Returns:
            Dictionary with results including analysis and proposal
        """
        with agent_logger("System"):
            logger.info("Starting governance workflow with CrewAI")
            
        result = self.crew.kickoff()
        
        with agent_logger("System"):
            logger.info("Governance workflow completed")
            
        return {
            "analysis": result[0],
            "proposal": result[1]
        } 