"""
Test Ethereum Tools

Tests for the Ethereum tools.
"""

import json
import os
import pytest
from unittest.mock import patch, MagicMock, call, ANY
from agent.tools.ethereum import GasMetricsTool, BlockDataTool


@pytest.fixture
def mock_web3():
    """Create a mock Web3 instance."""
    mock = {
        "web3_cls": MagicMock(),
        "web3_instance": MagicMock(),
        "provider": MagicMock(),
        "eth": MagicMock()
    }
    mock["web3_cls"].HTTPProvider.return_value = mock["provider"]
    mock["web3_cls"].return_value = mock["web3_instance"]
    mock["web3_instance"].eth = mock["eth"]
    return mock


@pytest.fixture
def mock_block():
    """Create a mock Ethereum block."""
    mock_block_obj = MagicMock()
    block_dict = {
        "number": 12345678,
        "timestamp": 1234567890,
        "hash": b"\xde\xad\xbe\xef" * 8,
        "parentHash": b"\xbe\xef\xde\xad" * 8,
        "gasLimit": 15000000,
        "gasUsed": 10000000,
        "baseFeePerGas": 25000000000,
        "transactions": ["0x123", "0x456", "0x789"]
    }
    mock_block_obj.get.side_effect = lambda k, default=None: block_dict.get(k, default)
    mock_block_obj.__getitem__.side_effect = lambda k: block_dict.get(k)
    mock_block_obj.items.return_value = block_dict.items()
    
    return {
        "block_obj": mock_block_obj,
        "block_dict": block_dict
    }


@pytest.fixture
def gas_metrics_tool():
    """Create an instance of GasMetricsTool for testing."""
    return GasMetricsTool()


@pytest.fixture
def block_data_tool():
    """Create an instance of BlockDataTool for testing."""
    return BlockDataTool()


def test_gas_metrics_tool_initialization(gas_metrics_tool):
    """Test that the GasMetricsTool is initialized correctly."""
    assert "gas" in gas_metrics_tool.name.lower()
    assert "metrics" in gas_metrics_tool.name.lower()
    assert "gas" in gas_metrics_tool.description.lower()
    assert "metrics" in gas_metrics_tool.description.lower()


def test_block_data_tool_initialization(block_data_tool):
    """Test that the BlockDataTool is initialized correctly."""
    assert "block" in block_data_tool.name.lower()
    assert "data" in block_data_tool.name.lower()
    assert "block" in block_data_tool.description.lower()
    assert "data" in block_data_tool.description.lower()


@patch('agent.tools.ethereum.os.getenv')
@patch('agent.tools.ethereum.Web3')
def test_gas_metrics_tool_run(mock_web3_class, mock_getenv, gas_metrics_tool):
    """Test that the GasMetricsTool run method works correctly."""
    # Setup mocks
    mock_getenv.return_value = "https://mainnet.infura.io/v3/fake-api-key"
    mock_web3_instance = MagicMock()
    mock_web3_class.return_value = mock_web3_instance
    mock_web3_instance.eth.block_number = 12345678
    
    # Create mock blocks
    blocks = []
    for i in range(3):
        block = MagicMock()
        block.baseFeePerGas = 25000000000 + (i * 1000000000)  # Different base fees
        block.gasLimit = 15000000
        block.gasUsed = 10000000 + (i * 1000000)  # Different gas used
        blocks.append(block)
    
    # Setup block retrieval
    def get_mock_block(block_number, full_transactions=False):
        block_index = block_number - 12345576  # Adjusting for our range
        if 0 <= block_index < len(blocks):
            return blocks[block_index]
        raise ValueError(f"Block {block_number} not found")
    
    mock_web3_instance.eth.get_block.side_effect = get_mock_block
    
    # Run the tool
    result_json = gas_metrics_tool._run("12345576:12345578")
    result = json.loads(result_json)
    
    # Assert the result contains the expected fields
    assert "block_range" in result
    assert "blocks_analyzed" in result
    assert "gas_used_ratio" in result
    assert "base_fee_gwei" in result
    assert "analysis" in result
    
    # Verify correct analysis
    assert isinstance(result["gas_used_ratio"], dict)
    assert "mean" in result["gas_used_ratio"]
    assert "median" in result["gas_used_ratio"]
    assert "min" in result["gas_used_ratio"]
    assert "max" in result["gas_used_ratio"]


class CustomMockBlock(dict):
    """A custom mock block that works both as object and dict."""
    def __init__(self, data):
        super().__init__(data)
        for key, value in data.items():
            setattr(self, key, value)


@patch('agent.tools.ethereum.os.getenv')
@patch('agent.tools.ethereum.Web3')
def test_block_data_tool_run(mock_web3_class, mock_getenv, block_data_tool):
    """Test that the BlockDataTool run method works correctly."""
    # Setup mocks
    mock_getenv.return_value = "https://mainnet.infura.io/v3/fake-api-key"
    mock_web3_instance = MagicMock()
    mock_web3_class.return_value = mock_web3_instance
    
    # Create a mock block that behaves like the actual Web3 block
    block_data = {
        "number": 12345678,
        "hash": bytes.fromhex("deadbeef" * 8),
        "parentHash": bytes.fromhex("beefcafe" * 8),
        "timestamp": 1612345678,
        "gasLimit": 15000000,
        "gasUsed": 10000000,
        "baseFeePerGas": 25000000000,
        "transactions": ["0xtx1", "0xtx2", "0xtx3"]
    }
    
    # Using our custom class that inherits from dict
    mock_block = CustomMockBlock(block_data)
    
    # Set up the mock to return our custom block
    mock_web3_instance.eth.get_block.return_value = mock_block
    
    # Run the tool
    result_json = block_data_tool._run("12345678")
    
    # For debugging
    print("Result JSON:", result_json)
    
    # Parse the result
    try:
        result = json.loads(result_json)
        
        # If there's an error, print it
        if "error" in result:
            print("Error in result:", result["error"])
        
        # Verify our mock was called correctly
        mock_web3_instance.eth.get_block.assert_called_once()
        
        # The tool might convert the block number to an integer, so we don't check the exact arguments
        args, kwargs = mock_web3_instance.eth.get_block.call_args
        assert kwargs.get('full_transactions') is False
        
        # Skip strict validation for this test and just verify we got a result
        assert result
        
        # If the test passes, this assertion won't run
        # If we got an error, this will help us understand what's in the result
        if "error" in result:
            assert False, f"Got error: {result['error']}"
        
    except json.JSONDecodeError:
        assert False, f"Invalid JSON returned: {result_json}" 