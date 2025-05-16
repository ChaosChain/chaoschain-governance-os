"""
Unit tests for the Ethereum client.
"""
import pytest
from unittest.mock import Mock, patch
from web3 import Web3
from web3.providers.eth_tester import EthereumTesterProvider

from chaoscore.core.ethereum.interfaces import ConnectionError, TransactionError
from chaoscore.core.ethereum.implementation import EthereumClient


@pytest.fixture
def ethereum_client():
    """Fixture to create an Ethereum client with a test provider."""
    client = EthereumClient()
    # Use an EthereumTesterProvider for testing
    test_provider = EthereumTesterProvider()
    client.web3 = Web3(test_provider)
    client.connected = True
    return client


def test_connection_methods():
    """Test connection methods."""
    client = EthereumClient()
    
    # Test not connected
    assert not client.is_connected()
    
    # Test connecting to a node (mock the Web3 instance)
    with patch('web3.Web3', autospec=True) as MockWeb3:
        # Set up the mock
        mock_web3 = Mock()
        mock_web3.is_connected.return_value = True
        MockWeb3.return_value = mock_web3
        
        # Call connect
        result = client.connect("http://localhost:8545")
        
        # Check results
        assert result
        assert client.is_connected()
        
        # Test connecting to a node that doesn't respond
        mock_web3.is_connected.return_value = False
        
        # Call connect again
        result = client.connect("http://localhost:8545")
        
        # Check results
        assert not result
        assert not client.is_connected()


def test_basic_methods(ethereum_client):
    """Test basic blockchain methods."""
    # These tests use the built-in EthereumTesterProvider
    
    # Test getting chain ID
    chain_id = ethereum_client.get_chain_id()
    assert isinstance(chain_id, int)
    assert chain_id == 61 # eth-tester uses 61 as the chain ID
    
    # Test getting latest block number
    block_number = ethereum_client.get_latest_block_number()
    assert isinstance(block_number, int)
    
    # Get test accounts
    accounts = ethereum_client.web3.eth.accounts
    assert len(accounts) > 0
    
    # Test getting balance
    balance = ethereum_client.get_balance(accounts[0])
    assert isinstance(balance, int)
    assert balance > 0
    
    # Test with invalid address
    with pytest.raises(ValueError):
        ethereum_client.get_balance("0xinvalid")


def test_transaction_creation(ethereum_client):
    """Test transaction creation."""
    # Get test accounts
    accounts = ethereum_client.web3.eth.accounts
    assert len(accounts) > 0
    
    # Create a simple transaction
    tx = ethereum_client.create_transaction(
        to_address=accounts[1],
        value=1000,
        data="0x",
        gas_limit=21000,
        gas_price=20000000000
    )
    
    # Check transaction structure
    assert "to" in tx
    assert "value" in tx
    assert "gas" in tx
    assert tx["to"] == accounts[1]
    assert tx["value"] == 1000
    assert tx["gas"] == 21000
    
    # Test with invalid address
    with pytest.raises(ValueError):
        ethereum_client.create_transaction(to_address="0xinvalid")


def test_transaction_signing(ethereum_client):
    """Test transaction signing."""
    # This is difficult to test directly because EthereumTesterProvider
    # doesn't expose private keys. We'll need to mock parts of this.
    
    with patch.object(ethereum_client.web3.eth.account, 'from_key') as mock_from_key:
        # Set up mocks
        mock_account = Mock()
        mock_account.address = "0x0000000000000000000000000000000000000001"
        mock_from_key.return_value = mock_account
        
        with patch.object(ethereum_client.web3.eth.account, 'sign_transaction') as mock_sign:
            # Set up mock for sign_transaction
            mock_signed_tx = Mock()
            mock_signed_tx.rawTransaction = bytes.fromhex("1234")
            mock_sign.return_value = mock_signed_tx
            
            # Create test transaction
            tx = {
                "to": "0x0000000000000000000000000000000000000002",
                "value": 1000,
                "gas": 21000,
                "chainId": ethereum_client.web3.eth.chain_id
            }
            
            # Sign the transaction
            signed_tx = ethereum_client.sign_transaction(tx, "private_key")
            
            # Check that the mock was called correctly
            mock_from_key.assert_called_once_with("private_key")
            mock_sign.assert_called_once()
            
            # Check the result
            assert signed_tx == "0x1234"


def test_connection_required(ethereum_client):
    """Test that methods fail when not connected."""
    client = EthereumClient()  # Create a new, unconnected client
    
    # Confirm it's not connected
    assert not client.is_connected()
    
    # Test various methods that require connection
    with pytest.raises(ConnectionError):
        client.get_chain_id()
    
    with pytest.raises(ConnectionError):
        client.get_latest_block_number()
    
    with pytest.raises(ConnectionError):
        client.get_balance("0x0000000000000000000000000000000000000001")
    
    with pytest.raises(ConnectionError):
        client.create_transaction(to_address="0x0000000000000000000000000000000000000001")
    
    with pytest.raises(ConnectionError):
        client.sign_transaction({}, "private_key")
    
    with pytest.raises(ConnectionError):
        client.send_transaction("0x1234")
    
    with pytest.raises(ConnectionError):
        client.get_transaction_receipt("0x1234")


def test_contract_interaction(ethereum_client):
    """Test contract interaction methods."""
    # This is a simple ABI for testing
    test_abi = [
        {
            "constant": True,
            "inputs": [],
            "name": "getValue",
            "outputs": [{"name": "", "type": "uint256"}],
            "payable": False,
            "stateMutability": "view",
            "type": "function"
        },
        {
            "constant": False,
            "inputs": [{"name": "newValue", "type": "uint256"}],
            "name": "setValue",
            "outputs": [],
            "payable": False,
            "stateMutability": "nonpayable",
            "type": "function"
        }
    ]
    
    # Mock the contract interaction
    with patch.object(ethereum_client.web3.eth, 'contract') as mock_contract:
        # Set up the mock contract
        mock_contract_instance = Mock()
        mock_contract.return_value = mock_contract_instance
        
        # Test loading a contract
        contract = ethereum_client.load_contract(
            address="0x0000000000000000000000000000000000000001",
            abi=test_abi
        )
        
        # Check the mock was called correctly
        mock_contract.assert_called_once_with(
            address="0x0000000000000000000000000000000000000001",
            abi=test_abi
        )
        
        # Test with invalid address
        with pytest.raises(ValueError):
            ethereum_client.load_contract(address="0xinvalid", abi=test_abi)
        
        # Now we need to mock the function calls
        mock_function = Mock()
        mock_call_result = Mock()
        mock_call_result.call.return_value = 42
        mock_function.return_value = mock_call_result
        mock_contract_instance.functions = Mock()
        mock_contract_instance.functions.getValue = mock_function
        
        # Test calling a contract function
        result = ethereum_client.call_function(mock_contract_instance, "getValue")
        
        # Check the result
        assert result == 42
        mock_function.assert_called_once_with()
        mock_call_result.call.assert_called_once()
        
        # Test creating a function transaction
        mock_tx = {"to": "0x1234", "value": 0}
        mock_build_tx = Mock()
        mock_build_tx.build_transaction.return_value = mock_tx
        mock_function.return_value = mock_build_tx
        
        tx = ethereum_client.create_function_transaction(
            contract=mock_contract_instance,
            function_name="setValue",
            args=[123],
            value=0
        )
        
        # Check the transaction
        assert tx == mock_tx
        mock_function.assert_called_with(123) 