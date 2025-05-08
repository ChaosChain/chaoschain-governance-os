"""
Gas Metrics Researcher Agent

This agent analyzes Ethereum gas metrics to identify optimization opportunities
for gas-related protocol parameters.
"""

from typing import Dict, Any
from crewai import Agent
from langchain.tools import BaseTool
from agent.tools.ethereum import GasMetricsTool, BlockDataTool

class GasMetricsResearcher:
    """
    Creates a CrewAI agent specialized in analyzing Ethereum gas metrics
    and identifying optimization opportunities.
    """
    
    def __init__(self, llm=None, verbose=False):
        """
        Initialize the gas metrics researcher agent.
        
        Args:
            llm: Language model to use (defaults to CrewAI default)
            verbose: Enable verbose logging
        """
        self.tools = [
            GasMetricsTool(),
            BlockDataTool()
        ]
        
        self.agent = Agent(
            role="Gas Metrics Researcher",
            goal="Analyze Ethereum gas data to identify optimization opportunities for gas-related parameters",
            backstory="""You are an expert in Ethereum gas mechanics and EIP-1559 fee market.
            You specialize in analyzing historical gas usage patterns to identify potential
            improvements to gas-related parameters. You have deep knowledge of how gas limits,
            base fees, and priority fees affect network performance and user experience.""",
            tools=self.tools,
            verbose=verbose,
            llm=llm
        )
    
    def get_agent(self):
        """
        Returns the CrewAI agent instance
        """
        return self.agent 