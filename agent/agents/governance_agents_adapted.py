"""
Adapted Governance Agents

This module implements a version of the GovernanceAgents class that uses
the ChaosCore platform components through the adapter layer.
"""

import os
import uuid
from typing import Dict, Any, Optional
from crewai import Crew, Task, Agent

from agent.agents.researcher.gas_metrics_researcher import GasMetricsResearcher
from agent.agents.developer.parameter_optimizer import ParameterOptimizer

from adapters import (
    AgentRegistryAdapter,
    ProofOfAgencyAdapter,
    SecureExecutionAdapter,
    ReputationAdapter,
    StudioAdapter
)


class AdaptedGovernanceAgents:
    """
    A CrewAI team for blockchain governance, combining researcher and developer agents
    to generate parameter optimization proposals.
    
    This version uses the ChaosCore platform components through the adapter layer.
    """
    
    def __init__(
        self,
        agent_registry_adapter: AgentRegistryAdapter,
        proof_of_agency_adapter: ProofOfAgencyAdapter,
        secure_execution_adapter: SecureExecutionAdapter,
        reputation_adapter: ReputationAdapter = None,
        studio_adapter: StudioAdapter = None,
        llm=None,
        verbose=False
    ):
        """
        Initialize the governance agents.
        
        Args:
            agent_registry_adapter: Adapter for the agent registry
            proof_of_agency_adapter: Adapter for the proof of agency framework
            secure_execution_adapter: Adapter for the secure execution environment
            reputation_adapter: Optional adapter for the reputation system
            studio_adapter: Optional adapter for the studio framework
            llm: Language model to use (defaults to CrewAI default)
            verbose: Enable verbose logging
        """
        self.verbose = verbose
        self.llm = llm
        
        # Store adapters
        self._agent_registry = agent_registry_adapter
        self._proof_of_agency = proof_of_agency_adapter
        self._secure_execution = secure_execution_adapter
        self._reputation = reputation_adapter
        self._studio = studio_adapter
        
        # Initialize agents
        self.researcher = GasMetricsResearcher(llm=llm, verbose=verbose).get_agent()
        self.developer = ParameterOptimizer(llm=llm, verbose=verbose).get_agent()
        
        # Register agents in the registry
        self._register_agents()
        
        # Create the crew
        self.crew = Crew(
            agents=[self.researcher, self.developer],
            tasks=self._create_tasks(),
            verbose=verbose
        )
    
    def _register_agents(self):
        """Register the agents in the agent registry."""
        agent_data = {
            "researcher": {
                "email": f"researcher-{uuid.uuid4()}@chaoscore.io",
                "name": "Gas Metrics Researcher",
            },
            "developer": {
                "email": f"developer-{uuid.uuid4()}@chaoscore.io",
                "name": "Parameter Optimizer",
            }
        }
        
        self.agent_ids = self._agent_registry.register_governance_agents(agent_data)
    
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
        
        This method:
        1. Logs the start of the workflow as an action
        2. Runs the CrewAI workflow
        3. Records the results
        4. Updates agent reputation
        5. Returns the results
        
        Returns:
            Dictionary with results including analysis, proposal, and action records
        """
        # Log the start of the research action
        research_action_id = self._proof_of_agency.log_action(
            agent_id=self.agent_ids["researcher"],
            action_type="ANALYZE",
            description="Analyze Ethereum gas metrics for optimization opportunities",
            data={"task_type": "research", "metrics_source": "ethereum"}
        )
        
        # Run the CrewAI workflow
        crew_result = self.crew.kickoff()
        analysis_result = crew_result[0]
        proposal_result = crew_result[1]
        
        # Record the outcome of the research action
        self._proof_of_agency.record_outcome(
            action_id=research_action_id,
            success=True,
            results={"analysis": analysis_result},
            impact_score=0.8
        )
        
        # Verify the research action
        self._proof_of_agency.verify_action(
            action_id=research_action_id,
            verifier_id=self.agent_ids["developer"],
            verification_data={"verified_at": str(uuid.uuid4())}
        )
        
        # Anchor the research action
        self._proof_of_agency.anchor_action(research_action_id)
        
        # Log the proposal development action
        proposal_action_id = self._proof_of_agency.log_action(
            agent_id=self.agent_ids["developer"],
            action_type="CREATE",
            description="Generate parameter optimization proposal based on gas metrics analysis",
            data={
                "task_type": "proposal_development",
                "research_action_id": research_action_id
            }
        )
        
        # Securely run simulation on the proposal
        simulation_data = {"proposal": proposal_result}
        simulation_result = self._secure_execution.run(
            self._simulate_proposal,
            proposal_data=simulation_data
        )
        
        # Record the outcome of the proposal action with the attestation hash
        attestation_hash = simulation_result["attestation"]["hash"]
        self._proof_of_agency.record_outcome(
            action_id=proposal_action_id,
            success=True,
            results={
                "proposal": proposal_result,
                "simulation": simulation_result["result"],
                "attestation_hash": attestation_hash
            },
            impact_score=0.9
        )
        
        # Verify the proposal action
        self._proof_of_agency.verify_action(
            action_id=proposal_action_id,
            verifier_id=self.agent_ids["researcher"],
            verification_data={"attestation_hash": attestation_hash}
        )
        
        # Anchor the proposal action
        self._proof_of_agency.anchor_action(proposal_action_id)
        
        # Update reputation if adapter is available
        reputation_updates = {}
        if self._reputation:
            for role, agent_id in self.agent_ids.items():
                # Update reputation based on the completed action
                action_id = research_action_id if role == "researcher" else proposal_action_id
                reputation_update = self._reputation.update_agent_reputation_after_action(
                    agent_id=agent_id,
                    action_id=action_id
                )
                reputation_updates[role] = reputation_update
        
        return {
            "analysis": analysis_result,
            "proposal": proposal_result,
            "simulation": simulation_result["result"] if "result" in simulation_result else None,
            "actions": {
                "research_action_id": research_action_id,
                "proposal_action_id": proposal_action_id
            },
            "attestation": {
                "hash": attestation_hash,
                "data": simulation_result["attestation"]["data"] if "attestation" in simulation_result else None
            },
            "reputation": reputation_updates
        }
    
    def _simulate_proposal(self, proposal_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulate the effects of a proposal.
        
        This method is executed in the secure execution environment.
        
        Args:
            proposal_data: The proposal data to simulate
            
        Returns:
            Dictionary with simulation results
        """
        from simulation.sim_harness import SimulationHarness
        
        # Extract parameters from the proposal
        proposal = proposal_data.get("proposal", {})
        parameters = {}
        
        # Look for parameter values in the proposal text
        if isinstance(proposal, str):
            # Very simple extraction - in a real system this would be more sophisticated
            if "gas_limit:" in proposal or "gas limit:" in proposal:
                try:
                    # Extract gas limit value
                    gas_limit_text = proposal.split("gas limit:")[1].split("\n")[0].strip()
                    gas_limit = int(gas_limit_text.replace(",", ""))
                    parameters["gas_limit"] = gas_limit
                except:
                    pass
                
            if "base fee max change denominator:" in proposal or "base_fee_max_change_denominator:" in proposal:
                try:
                    # Extract denominator value
                    key = "base fee max change denominator:" if "base fee max change denominator:" in proposal else "base_fee_max_change_denominator:"
                    denominator_text = proposal.split(key)[1].split("\n")[0].strip()
                    denominator = int(denominator_text)
                    parameters["base_fee_max_change_denominator"] = denominator
                except:
                    pass
        elif isinstance(proposal, dict):
            # If the proposal is already structured, use its parameters
            parameters = proposal.get("parameters", {})
        
        # Default parameters if none were found
        if not parameters:
            parameters = {
                "gas_limit": 15000000,
                "base_fee_max_change_denominator": 8
            }
        
        # Add simulation configuration
        parameters["simulation_blocks"] = 100
        
        # Create and run the simulation
        harness = SimulationHarness(
            gas_limit=parameters.get("gas_limit", 15000000),
            base_fee_per_gas=parameters.get("base_fee_per_gas", 10 * 10**9),
            fee_denominator=parameters.get("base_fee_max_change_denominator", 8)
        )
        
        # Run the simulation
        simulation_result = harness.run_simulation(parameters)
        
        return simulation_result 