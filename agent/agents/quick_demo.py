#!/usr/bin/env python
"""
Quick Demo of Agent Team

This module provides a simplified demo of the agent-based governance system
without requiring external API calls.
"""

import os
import random
from typing import Dict, Any, Optional, List
from crewai import Crew, Agent, Task
from pydantic import BaseModel


class MetricsAnalysis(BaseModel):
    """Model for gas metrics analysis results"""
    avg_gas_used: float
    avg_base_fee: float
    fee_volatility: float
    optimization_targets: List[str]
    block_range: Dict[str, int]
    
    
class ProposalParameters(BaseModel):
    """Model for proposal parameters"""
    gas_limit_adjustment: float
    base_fee_adjustment: float
    adjustment_quotient: int
    target_block_utilization: float
    
    
class DemoResearcher:
    """Demo researcher agent that provides deterministic analysis"""
    
    def __init__(self, llm=None, verbose=False):
        """Initialize the demo researcher"""
        self.verbose = verbose
        self.llm = llm
    
    def get_agent(self) -> Agent:
        """Get the CrewAI agent for the researcher"""
        return Agent(
            role="Gas Metrics Researcher",
            goal="Analyze blockchain gas metrics to identify optimization opportunities",
            backstory="""
            You are an expert data scientist specializing in blockchain metrics analysis.
            You have years of experience analyzing gas usage patterns and fee markets on 
            Ethereum and other EVM blockchains. You're known for your ability to identify
            subtle patterns in blockchain data and translate them into actionable insights.
            """,
            verbose=self.verbose,
            llm=self.llm,
            allow_delegation=False
        )
    
    def analyze_gas_metrics(self) -> str:
        """Simulate gas metrics analysis with deterministic output"""
        # Create a deterministic analysis
        analysis = MetricsAnalysis(
            avg_gas_used=0.82,
            avg_base_fee=23.5,
            fee_volatility=0.68,
            optimization_targets=["Gas limit", "Base fee adjustment mechanism"],
            block_range={"start": 18500000, "end": 18500100}
        )
        
        # Format the analysis as a detailed report
        report = f"""# Gas Metrics Analysis

## Executive Summary
After analyzing {analysis.block_range["end"] - analysis.block_range["start"]} blocks 
(from {analysis.block_range["start"]} to {analysis.block_range["end"]}), I've identified 
several optimization opportunities for the blockchain's gas parameters.

## Key Metrics
- Average gas used ratio: {analysis.avg_gas_used:.2f} (target range: 0.5-0.8)
- Average base fee: {analysis.avg_base_fee:.1f} gwei
- Fee volatility index: {analysis.fee_volatility:.2f} (moderate)

## Optimization Opportunities
1. The gas used ratio is consistently above the target range, suggesting the gas limit 
   could be adjusted to improve throughput while maintaining reasonable fees.
2. Base fee adjustment mechanism is too aggressive, leading to higher volatility than 
   necessary during periods of high demand.
3. A more gradual fee adjustment quotient could improve predictability for users.

## Recommendation
I recommend focusing optimization efforts on the following parameters:
{", ".join(analysis.optimization_targets)}

These changes could lead to approximately 12% improvement in fee predictability and 
7% increase in effective throughput during peak usage periods.
"""
        return report


class DemoOptimizer:
    """Demo parameter optimizer agent that provides deterministic proposals"""
    
    def __init__(self, llm=None, verbose=False):
        """Initialize the demo optimizer"""
        self.verbose = verbose
        self.llm = llm
    
    def get_agent(self) -> Agent:
        """Get the CrewAI agent for the optimizer"""
        return Agent(
            role="Parameter Optimizer",
            goal="Develop and simulate parameter optimization proposals",
            backstory="""
            You are a seasoned blockchain engineer with deep expertise in consensus 
            parameter optimization. You've worked on multiple L1 and L2 blockchains,
            fine-tuning their parameters for optimal performance, security, and user 
            experience. Your specialty is building simulation models to predict the 
            effects of parameter changes before they're implemented.
            """,
            verbose=self.verbose,
            llm=self.llm,
            allow_delegation=False
        )
    
    def create_proposal(self, analysis: str) -> str:
        """Create a deterministic proposal based on analysis"""
        # Create deterministic parameters
        params = ProposalParameters(
            gas_limit_adjustment=1.15,
            base_fee_adjustment=0.85,
            adjustment_quotient=12,  # Was 8 in EIP-1559
            target_block_utilization=0.75
        )
        
        # Format the proposal
        proposal = f"""# Parameter Optimization Proposal

## Overview
Based on the gas metrics analysis, I propose the following parameter adjustments to 
improve throughput and fee predictability.

## Proposed Parameters
1. Gas Limit Adjustment: +{(params.gas_limit_adjustment-1)*100:.0f}%
   - Current: ~30M gas/block
   - Proposed: ~{30*params.gas_limit_adjustment:.1f}M gas/block
   
2. Base Fee Adjustment: {params.base_fee_adjustment:.2f}x current rate
   - Reduces the intensity of base fee changes during demand spikes
   
3. EIP-1559 Adjustment Quotient: {params.adjustment_quotient} (currently 8)
   - Makes fee changes more gradual and predictable
   
4. Target Block Utilization: {params.target_block_utilization:.2f} (currently 0.5)
   - Sets optimal gas used ratio for the network

## Expected Benefits
- Improved fee predictability (est. 15% reduction in volatility)
- Higher throughput during peak demand (+10-12%)
- Better user experience due to more consistent transaction confirmation times
- More efficient market for block space

## Risks and Mitigations
- Risk: Higher gas limit could increase state growth rate
  - Mitigation: Monitor state growth and adjust if necessary
  
- Risk: More gradual fee adjustment could lead to longer periods of congestion
  - Mitigation: The higher gas limit compensates by providing more capacity

## Simulation Results
Simulations show these parameters would have reduced average fees by 8.5% during 
the last network congestion event, while increasing transaction throughput by 11.2%.

The parameters were tested against historical data from the past 3 months and 
demonstrated consistent improvements in both normal and high-demand scenarios.
"""
        return proposal


class QuickDemo:
    """
    Quick demo of the agent team for governance without external API calls.
    """
    
    def __init__(self, llm=None, verbose=False):
        """
        Initialize the quick demo team.
        
        Args:
            llm: Language model to use (defaults to CrewAI default)
            verbose: Enable verbose logging
        """
        self.verbose = verbose
        self.llm = llm
        
        # Initialize agents
        self.researcher = DemoResearcher(llm=llm, verbose=verbose).get_agent()
        self.developer = DemoOptimizer(llm=llm, verbose=verbose).get_agent()
        
        # Create the crew
        self.crew = Crew(
            agents=[self.researcher, self.developer],
            tasks=self._create_tasks(),
            verbose=verbose
        )
    
    def _create_tasks(self) -> list:
        """
        Create the tasks for the demo team.
        
        Returns:
            List of CrewAI tasks
        """
        # Define the tasks
        research_task = Task(
            description="""
            Analyze Ethereum gas metrics to identify potential optimization opportunities.
            
            Use the analyze_gas_metrics method to retrieve gas metrics data and provide analysis.
            """,
            agent=self.researcher,
            expected_output="A detailed analysis of gas metrics with identified optimization opportunities",
            tools=[self._analyze_gas_metrics]
        )
        
        proposal_task = Task(
            description="""
            Generate a parameter optimization proposal based on the researcher's findings.
            
            Review the researcher's analysis and use the create_proposal method to generate 
            an optimized parameter proposal.
            """,
            agent=self.developer,
            expected_output="A detailed parameter optimization proposal with simulation results",
            context=[research_task],
            tools=[self._create_proposal]
        )
        
        return [research_task, proposal_task]
    
    def _analyze_gas_metrics(self) -> str:
        """Tool for the researcher to analyze gas metrics"""
        return DemoResearcher().analyze_gas_metrics()
    
    def _create_proposal(self, analysis: str) -> str:
        """Tool for the developer to create a proposal"""
        return DemoOptimizer().create_proposal(analysis)
    
    def run(self) -> Dict[str, Any]:
        """
        Run the demo workflow.
        
        Returns:
            Dictionary with results including analysis and proposal
        """
        result = self.crew.kickoff()
        return {
            "analysis": result[0],
            "proposal": result[1]
        }


if __name__ == "__main__":
    # Initialize the quick demo team
    demo = QuickDemo()
    
    # Run the demo
    result = demo.run()
    
    # Print the results
    print("\nResults:")
    print(f"Analysis: {result['analysis']}")
    print(f"Proposal: {result['proposal']}") 