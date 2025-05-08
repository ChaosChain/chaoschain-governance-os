"""
Tests for the simulation harness.
"""

import pytest
from simulation import SimulationHarness, create_simulation


@pytest.fixture
def sample_proposal_data():
    """
    Create a sample proposal data for testing.
    
    Returns:
        Sample proposal data
    """
    return {
        "proposal_id": 42,
        "title": "Gas Limit Adjustment",
        "description": "Adjust gas limit for EIP-1559",
        "gas_adjustment": 1.2,
        "fee_adjustment": 0.9
    }


def test_simulation_harness_initialization():
    """Test that the SimulationHarness initializes correctly."""
    harness = SimulationHarness(
        transaction_count=50,
        gas_limit=10000000,
        base_fee_per_gas=5 * 10**9,
        fee_denominator=10
    )
    
    assert harness.transaction_count == 50
    assert harness.gas_limit == 10000000
    assert harness.base_fee_per_gas == 5 * 10**9
    assert harness.fee_denominator == 10
    assert harness.simulation_id is not None


def test_generate_address():
    """Test address generation."""
    harness = SimulationHarness()
    address = harness._generate_address()
    
    assert address.startswith("0x")
    assert len(address) == 42  # 0x + 40 hex chars
    assert all(c in "0123456789abcdef" for c in address[2:])


def test_generate_transaction():
    """Test transaction generation."""
    harness = SimulationHarness()
    tx = harness.generate_transaction()
    
    # Check basic transaction structure
    assert "from" in tx
    assert "to" in tx
    assert "value" in tx
    assert "gasPrice" in tx
    assert "gasLimit" in tx
    assert "gasUsed" in tx
    assert "data" in tx
    assert "nonce" in tx
    assert "hash" in tx
    
    # Check that gas values make sense
    assert int(tx["gasUsed"], 16) <= int(tx["gasLimit"], 16)


def test_generate_transactions_batch():
    """Test generating a batch of transactions."""
    harness = SimulationHarness(transaction_count=10)
    txs = harness.generate_transactions()
    
    assert len(txs) == 10
    assert all(isinstance(tx, dict) for tx in txs)


def test_run_simulation(sample_proposal_data):
    """Test running a simulation."""
    harness = SimulationHarness(transaction_count=5)
    result = harness.run_simulation(sample_proposal_data)
    
    # Check that the result contains the expected fields
    assert "simulation_id" in result
    assert "proposal_id" in result
    assert result["proposal_id"] == 42
    assert "timestamp" in result
    assert "transaction_count" in result
    assert result["transaction_count"] == 5
    assert "gas_factor" in result
    assert result["gas_factor"] == 1.2  # From gas_adjustment in proposal data
    assert "fee_factor" in result
    assert result["fee_factor"] == 0.9  # From fee_adjustment in proposal data
    assert "transactions" in result
    assert len(result["transactions"]) == 5


def test_transaction_adjustments(sample_proposal_data):
    """Test that transactions are properly adjusted based on proposal data."""
    harness = SimulationHarness(transaction_count=1)
    result = harness.run_simulation(sample_proposal_data)
    
    tx = result["transactions"][0]
    
    # Check that adjusted values are present
    assert "adjustedGasLimit" in tx
    assert "adjustedGasUsed" in tx
    assert "adjustedGasPrice" in tx
    assert "originalCost" in tx
    assert "adjustedCost" in tx
    assert "costDifference" in tx
    
    # Check adjustment logic
    gas_limit = int(tx["gasLimit"], 16)
    adjusted_gas_limit = int(tx["adjustedGasLimit"], 16)
    assert adjusted_gas_limit == int(gas_limit * 1.2)
    
    gas_price = int(tx["gasPrice"], 16)
    adjusted_gas_price = int(tx["adjustedGasPrice"], 16)
    assert adjusted_gas_price == int(gas_price * 0.9)


def test_create_simulation_helper(sample_proposal_data):
    """Test the create_simulation helper function."""
    result = create_simulation(
        proposal_data=sample_proposal_data,
        transaction_count=3,
        gas_limit=8000000,
        base_fee_per_gas=2 * 10**9,
        fee_denominator=8
    )
    
    assert "simulation_id" in result
    assert "transaction_count" in result
    assert result["transaction_count"] == 3
    assert "gas_limit" in result
    assert result["gas_limit"] == 8000000
    assert "base_fee_per_gas" in result
    assert result["base_fee_per_gas"] == 2 * 10**9
    assert "fee_denominator" in result
    assert result["fee_denominator"] == 8 