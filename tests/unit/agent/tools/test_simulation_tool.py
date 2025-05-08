"""
Test Simulation Tool

Tests for the simulation tool.
"""

import json
import pytest
from unittest.mock import patch, MagicMock
from agent.tools.simulation import SimulationTool


@pytest.fixture
def simulation_tool():
    """Create a SimulationTool instance for testing."""
    return SimulationTool()


def test_simulation_tool_initialization():
    """Test that the SimulationTool initializes correctly."""
    tool = SimulationTool()
    assert tool.name == "parameter_simulator"
    assert "simulate" in tool.description.lower()
    assert "parameter" in tool.description.lower()


def test_simulation_tool_run_with_valid_parameters(simulation_tool):
    """Test that the SimulationTool run method works correctly with valid parameters."""
    # Valid parameters
    params = {
        "gas_limit": 30_000_000,
        "base_fee_max_change_denominator": 16,
        "simulation_blocks": 100
    }
    
    # Run the tool
    result_json = simulation_tool._run(json.dumps(params))
    result = json.loads(result_json)
    
    # Verify result structure
    assert "simulation_config" in result
    assert "baseline" in result
    assert "modified" in result
    assert "comparison" in result
    assert "analysis" in result
    
    # Verify the simulation config contains our parameters
    assert result["simulation_config"]["parameters"]["gas_limit"] == 30_000_000
    assert result["simulation_config"]["parameters"]["base_fee_max_change_denominator"] == 16
    assert result["simulation_config"]["blocks_simulated"] == 100


def test_simulation_tool_run_with_invalid_json(simulation_tool):
    """Test that the SimulationTool handles invalid JSON input."""
    # Run the tool with invalid JSON
    result_json = simulation_tool._run("invalid json")
    result = json.loads(result_json)
    
    # Verify error handling
    assert "error" in result
    assert "Invalid JSON format" in result["error"]


def test_simulation_tool_run_with_non_dict_parameters(simulation_tool):
    """Test that the SimulationTool handles non-dict parameters."""
    # Run the tool with non-dict parameters
    result_json = simulation_tool._run(json.dumps(["not", "a", "dict"]))
    result = json.loads(result_json)
    
    # Verify error handling
    assert "error" in result
    assert "must be a JSON object" in result["error"]


def test_simulation_tool_run_with_invalid_simulation_blocks(simulation_tool):
    """Test that the SimulationTool handles invalid simulation_blocks."""
    # Run the tool with invalid simulation_blocks
    result_json = simulation_tool._run(json.dumps({"gas_limit": 30_000_000, "simulation_blocks": -10}))
    result = json.loads(result_json)
    
    # Verify error handling
    assert "error" in result
    assert "simulation_blocks must be a positive integer" in result["error"]


def test_simulation_tool_gas_limit_effects(simulation_tool):
    """Test that the SimulationTool correctly models gas limit changes."""
    # Test with increased gas limit
    high_gas_params = {
        "gas_limit": 30_000_000,  # Double the mock "current" value
        "simulation_blocks": 100
    }
    
    high_gas_result = json.loads(simulation_tool._run(json.dumps(high_gas_params)))
    
    # Test with decreased gas limit
    low_gas_params = {
        "gas_limit": 10_000_000,  # Lower than the mock "current" value
        "simulation_blocks": 100
    }
    
    low_gas_result = json.loads(simulation_tool._run(json.dumps(low_gas_params)))
    
    # Verify that increasing gas limit decreases gas used ratio
    assert high_gas_result["modified"]["avg_gas_used_ratio"] < high_gas_result["baseline"]["avg_gas_used_ratio"]
    
    # Verify that decreasing gas limit increases gas used ratio
    assert low_gas_result["modified"]["avg_gas_used_ratio"] > low_gas_result["baseline"]["avg_gas_used_ratio"]


def test_simulation_tool_fee_denominator_effects(simulation_tool):
    """Test that the SimulationTool correctly models fee denominator changes."""
    # Test with increased denominator (reduced volatility)
    high_denominator_params = {
        "base_fee_max_change_denominator": 16,  # Higher than the default 8
        "simulation_blocks": 100
    }
    
    high_denominator_result = json.loads(simulation_tool._run(json.dumps(high_denominator_params)))
    
    # Test with decreased denominator (increased volatility)
    low_denominator_params = {
        "base_fee_max_change_denominator": 4,  # Lower than the default 8
        "simulation_blocks": 100
    }
    
    low_denominator_result = json.loads(simulation_tool._run(json.dumps(low_denominator_params)))
    
    # Verify that increasing denominator decreases fee volatility
    assert high_denominator_result["modified"]["fee_volatility"] < high_denominator_result["baseline"]["fee_volatility"]
    
    # Verify that decreasing denominator increases fee volatility
    assert low_denominator_result["modified"]["fee_volatility"] > low_denominator_result["baseline"]["fee_volatility"] 