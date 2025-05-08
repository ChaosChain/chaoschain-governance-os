"""
Parameter Optimizer Agent

This agent generates concrete parameter optimization proposals based on research findings.
"""

from typing import Dict, Any
from crewai import Agent
from langchain.tools import BaseTool
from agent.tools.simulation import SimulationTool

class ParameterOptimizer:
    """
    Creates a CrewAI agent specialized in generating and optimizing
    blockchain parameter proposals.
    """
    
    def __init__(self, llm=None, verbose=False):
        """
        Initialize the parameter optimizer agent.
        
        Args:
            llm: Language model to use (defaults to CrewAI default)
            verbose: Enable verbose logging
        """
        self.tools = [
            SimulationTool()
        ]
        
        self.agent = Agent(
            role="Blockchain Protocol Developer",
            goal="Create optimized parameter proposals based on research data",
            backstory="""You are an expert blockchain protocol developer with deep
            knowledge of Ethereum's mechanics and parameters. You specialize in
            analyzing research findings and translating them into concrete parameter
            optimization proposals. You have a deep understanding of the tradeoffs
            involved in parameter changes and can predict their likely effects on
            network performance, user experience, and security.""",
            tools=self.tools,
            verbose=verbose,
            llm=llm
        )
    
    def get_agent(self):
        """
        Returns the CrewAI agent instance
        """
        return self.agent 