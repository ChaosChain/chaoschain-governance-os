"""Unit tests for quick_demo.py EthereumRPCClient."""

import json
from unittest.mock import MagicMock, patch

import pytest

from agent.crew.quick_demo import EthereumRPCClient


@pytest.fixture
def mock_response():
    """Create a mock response."""
    mock = MagicMock()
    mock.raise_for_status = MagicMock()
    return mock


@pytest.fixture
def client():
    """Create an EthereumRPCClient instance."""
    return EthereumRPCClient("https://test.rpc.url")


def test_get_latest_block_number(client, mock_response):
    """Test get_latest_block_number method."""
    # Mock the response
    mock_response.json.return_value = {
        "jsonrpc": "2.0",
        "id": 1,
        "result": "0x100"
    }
    
    # Patch requests.post
    with patch("requests.post", return_value=mock_response):
        block_number = client.get_latest_block_number()
        
        # Assertions
        assert block_number == 256  # 0x100 in decimal
        assert client.request_id == 2


def test_get_block_by_number(client, mock_response):
    """Test get_block_by_number method."""
    # Mock the response
    mock_response.json.return_value = {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {
            "number": "0x100",
            "hash": "0xabcd...",
            "gasUsed": "0x5000",
            "gasLimit": "0x10000"
        }
    }
    
    # Patch requests.post
    with patch("requests.post", return_value=mock_response):
        block_data = client.get_block_by_number(256)
        
        # Assertions
        assert block_data["gasUsed"] == "0x5000"
        assert block_data["gasLimit"] == "0x10000"
        assert client.request_id == 2


def test_get_gas_price(client, mock_response):
    """Test get_gas_price method."""
    # Mock the response
    mock_response.json.return_value = {
        "jsonrpc": "2.0",
        "id": 1,
        "result": "0x3b9aca00"  # 1 Gwei = 1,000,000,000 wei
    }
    
    # Patch requests.post
    with patch("requests.post", return_value=mock_response):
        gas_price = client.get_gas_price()
        
        # Assertions
        assert gas_price == 1000000000  # 1 Gwei in wei
        assert client.request_id == 2


def test_rpc_error(client, mock_response):
    """Test handling of RPC errors."""
    # Mock the response
    mock_response.json.return_value = {
        "jsonrpc": "2.0",
        "id": 1,
        "error": {
            "code": -32601,
            "message": "Method not found"
        }
    }
    
    # Patch requests.post
    with patch("requests.post", return_value=mock_response):
        # Assertions
        with pytest.raises(Exception, match="RPC error"):
            client._call("invalid_method") 