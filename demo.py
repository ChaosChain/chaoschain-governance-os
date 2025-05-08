#!/usr/bin/env python
"""
ChaosChain Governance OS Demo

This script demonstrates the core functionality of the ChaosChain Governance OS
using deterministic data for a consistent demo experience.
"""

import time
import json
import sys
import os
from typing import Dict, Any

# Import configuration
from simulation.harness.config import DEMO_PROPOSAL, DEMO_SIMULATION_CONFIG
from verification.tee import phala_stub

# Import API models
from api.models import Base, engine
from api.db.session import get_db
from api.models.proposals import create_proposal, ProposalStatus, update_proposal_status
from api.models.crud import create_simulation_run, update_simulation_result, create_attestation

# Try to import rich for pretty logging
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich import print as rich_print
    console = Console()
    has_rich = True
except ImportError:
    has_rich = False
    console = None
    rich_print = print

# Configuration
VERBOSE = "--verbose" in sys.argv


def log(message: str, level: str = "INFO") -> None:
    """
    Log a message with optional styling.
    
    Args:
        message: Message to log
        level: Log level (INFO, SUCCESS, ERROR, WARNING)
    """
    timestamp = time.strftime("%H:%M:%S")
    
    if has_rich:
        color = {
            "INFO": "blue",
            "SUCCESS": "green",
            "ERROR": "red",
            "WARNING": "yellow",
            "DEBUG": "grey70"
        }.get(level, "white")
        
        if level == "DEBUG" and not VERBOSE:
            return
            
        console.print(f"[{timestamp}] ", end="")
        console.print(f"[{color}]{level}[/{color}]", end=" ")
        console.print(message)
    else:
        if level == "DEBUG" and not VERBOSE:
            return
        print(f"[{timestamp}] {level}: {message}")


def print_header(title: str) -> None:
    """
    Print a styled header.
    
    Args:
        title: Header title
    """
    if has_rich:
        console.print(Panel(title, style="bold magenta", expand=False))
    else:
        print(f"\n{'=' * 50}")
        print(f"{title.center(50)}")
        print(f"{'=' * 50}\n")


def run_demo() -> None:
    """Run the ChaosChain demo with deterministic data."""
    # Ensure database tables exist
    Base.metadata.create_all(bind=engine)
    
    # Print welcome message
    print_header("🔮 ChaosChain Governance OS Demo")
    log("Starting demo with deterministic data")
    
    # Step 1: Create a proposal
    log("Creating governance proposal...", "INFO")
    db = next(get_db())
    
    proposal = create_proposal(
        db=db,
        payload=DEMO_PROPOSAL,
        agent_sig="0x7365637572655f6167656e745f7369676e6174757265"
    )
    
    log(f"Created proposal {proposal.id}: {DEMO_PROPOSAL['title']}", "SUCCESS")
    log(f"Proposal parameters: gas_adjustment={DEMO_PROPOSAL['parameters']['gas_adjustment']}, fee_adjustment={DEMO_PROPOSAL['parameters']['fee_adjustment']}", "DEBUG")
    
    # Step 2: Run a simulation
    log("Running simulation with deterministic transactions...", "INFO")
    
    simulation_run = create_simulation_run(
        db=db,
        proposal_id=proposal.id,
        configuration=DEMO_SIMULATION_CONFIG
    )
    
    # Run simulation
    from simulation import create_simulation
    
    simulation_results = create_simulation(
        proposal_data={
            "proposal_id": proposal.id,
            **DEMO_PROPOSAL["parameters"]
        },
        transaction_count=DEMO_SIMULATION_CONFIG["transaction_count"],
        gas_limit=DEMO_SIMULATION_CONFIG["gas_limit"],
        base_fee_per_gas=DEMO_SIMULATION_CONFIG["base_fee_per_gas"],
        fee_denominator=DEMO_SIMULATION_CONFIG["fee_denominator"],
        use_predefined_transactions=True
    )
    
    # Update simulation results
    update_simulation_result(db, simulation_run.id, simulation_results)
    
    # Update proposal status
    update_proposal_status(db, proposal.id, ProposalStatus.SIMULATED)
    
    # Display simulation results
    gas_delta = simulation_results["gas_delta_percent"]
    fee_growth = simulation_results["fee_growth_bps"]
    
    log(f"Simulation completed for proposal {proposal.id}", "SUCCESS")
    log(f"✅ Simulation gas delta: {gas_delta:.2f}%, fee growth: {fee_growth:.1f} bps", "SUCCESS")
    
    # Step 3: Generate TEE attestation
    log("Generating TEE attestation...", "INFO")
    
    # Prepare attestation payload
    attestation_payload = {
        "proposal_id": proposal.id,
        "simulation_id": simulation_results["simulation_id"],
        "parameters": DEMO_PROPOSAL["parameters"],
        "summary": {
            "gas_delta_percent": gas_delta,
            "fee_growth_bps": fee_growth
        }
    }
    
    # Generate attestation
    attestation = phala_stub.generate_attestation(attestation_payload)
    
    # Store attestation in database
    db_attestation = create_attestation(
        db=db,
        proposal_id=proposal.id,
        enclave_id=attestation["enclave_id"],
        payload_hash=attestation["payload_hash"],
        signature=attestation["signature"],
        timestamp=attestation["timestamp"]
    )
    
    # Update proposal status
    update_proposal_status(db, proposal.id, ProposalStatus.VERIFIED)
    
    log(f"✅ Proposal {proposal.id} signed by enclave {attestation['enclave_id']} (Phala mock)", "SUCCESS")
    
    # Final summary
    print_header("📊 Demo Summary")
    
    rich_print(f"[bold]Proposal:[/bold] {DEMO_PROPOSAL['title']} (ID: {proposal.id})")
    rich_print(f"[bold]Status:[/bold] {ProposalStatus.VERIFIED}")
    rich_print(f"[bold]Simulation results:[/bold]")
    rich_print(f"  • Gas usage delta: [{'green' if gas_delta < 0 else 'red'}]{gas_delta:.2f}%[/]")
    rich_print(f"  • Fee growth: [{'red' if fee_growth > 0 else 'green'}]{fee_growth:.1f} bps[/]")
    rich_print(f"[bold]Attestation:[/bold]")
    rich_print(f"  • Enclave ID: {attestation['enclave_id']}")
    rich_print(f"  • Payload hash: {attestation['payload_hash'][:10]}...{attestation['payload_hash'][-6:]}")
    rich_print(f"  • Signature: {attestation['signature'][:10]}...{attestation['signature'][-6:]}")
    
    rich_print("\n[bold green]Demo completed successfully![/bold green]")


if __name__ == "__main__":
    run_demo() 