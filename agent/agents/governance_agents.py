"""
Governance Agents

This module implements a CrewAI team for blockchain governance,
combining researcher and developer agents to generate parameter optimization proposals.
"""

import os
from typing import Dict, Any, Optional
from crewai import Crew, Task, Agent

from agent.agents.researcher.gas_metrics_researcher import GasMetricsResearcher
from agent.agents.developer.parameter_optimizer import ParameterOptimizer


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
        
        # Initialize agents
        self.researcher = GasMetricsResearcher(llm=llm, verbose=verbose).get_agent()
        self.developer = ParameterOptimizer(llm=llm, verbose=verbose).get_agent()
        
        # Create the crew
        self.crew = Crew(
            agents=[self.researcher, self.developer],
            tasks=self._create_tasks(),
            verbose=verbose
        )
    
    def _create_tasks(self) -> list:
        """
        Create the tasks for the governance agents.
        
        Returns:
            List of CrewAI tasks
        """
        research_task = Task(
            description="""
            Analyze Ethereum gas metrics to identify potential optimization opportunities.
            
            Specific responsibilities:
            1. Collect gas metrics data from the Ethereum blockchain using the provided tools
            2. Analyze the data to identify patterns in gas usage, base fees, and other metrics
            3. Identify potential areas for parameter optimization (gas limit, EIP-1559 parameters)
            4. Provide a detailed report of your findings with supporting evidence
            
            Your analysis should consider at least 100 recent blocks and include specific metrics
            like average gas used ratio, base fee trends, and fee volatility.
            """,
            agent=self.researcher,
            expected_output="A detailed analysis of gas metrics with identified optimization opportunities"
        )
        
        proposal_task = Task(
            description="""
            Generate a parameter optimization proposal based on the researcher's findings.
            
            Specific responsibilities:
            1. Review the researcher's analysis of gas metrics and optimization opportunities
            2. Develop specific parameter change proposals (exact values for gas limit, etc.)
            3. Use the simulation tool to test your proposed parameter changes
            4. Refine your proposal based on simulation results
            5. Create a final proposal with clear justification, expected benefits, and risk assessment
            
            Your proposal should include specific parameter values, not just general recommendations.
            Consider both immediate effects and longer-term implications of your changes.
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
        result = self.crew.kickoff()
        return {
            "analysis": result[0],
            "proposal": result[1]
        } 