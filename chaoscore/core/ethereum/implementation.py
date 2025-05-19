"""
Ethereum Integration Implementation

This module provides concrete implementations of the Ethereum blockchain interfaces.
"""
from typing import Any, Dict, List, Optional, Union
import json
import os
from web3 import Web3
from web3.exceptions import Web3Exception

# Handle different web3 versions
try:
    from web3.middleware import geth_poa_middleware
    HAS_POA_MIDDLEWARE = True
except ImportError:
    HAS_POA_MIDDLEWARE = False

from .interfaces import (
    BlockchainClient,
    TransactionManager,
    ContractInteraction,
    EventMonitor,
    BlockchainIntegrationError,
    ConnectionError,
    TransactionError,
    ContractError
)


class EthereumClient(BlockchainClient, TransactionManager, ContractInteraction, EventMonitor):
    """
    Implementation of Ethereum blockchain client using web3.py.
    """
    
    def __init__(self):
        self.web3 = None
        self.connected = False
    
    def connect(self, endpoint_url: str) -> bool:
        """
        Connect to an Ethereum network.
        
        Args:
            endpoint_url: The URL of the Ethereum endpoint (HTTP, WebSocket, or IPC)
            
        Returns:
            bool: True if connection was successful, False otherwise
        """
        try:
            if endpoint_url.startswith('http'):
                provider = Web3.HTTPProvider(endpoint_url)
            elif endpoint_url.startswith('ws'):
                provider = Web3.WebsocketProvider(endpoint_url)
            else:
                provider = Web3.IPCProvider(endpoint_url)
            
            self.web3 = Web3(provider)
            
            # Inject middleware for POA chains like Sepolia if available
            if HAS_POA_MIDDLEWARE:
                self.web3.middleware_onion.inject(geth_poa_middleware, layer=0)
            
            # Check connection
            self.connected = self.web3.is_connected()
            
            return self.connected
        except Exception as e:
            self.web3 = None
            self.connected = False
            raise ConnectionError(f"Failed to connect to Ethereum network: {str(e)}")
    
    def get_chain_id(self) -> int:
        """
        Get the chain ID of the connected network.
        
        Returns:
            int: The chain ID
            
        Raises:
            ConnectionError: If not connected to a network
        """
        self._ensure_connected()
        return self.web3.eth.chain_id
    
    def get_latest_block_number(self) -> int:
        """
        Get the latest block number.
        
        Returns:
            int: The latest block number
            
        Raises:
            ConnectionError: If not connected to a network
        """
        self._ensure_connected()
        return self.web3.eth.block_number
    
    def get_balance(self, address: str) -> int:
        """
        Get the balance of an address.
        
        Args:
            address: The Ethereum address to check
            
        Returns:
            int: The balance in wei
            
        Raises:
            ConnectionError: If not connected to a network
            ValueError: If the address is invalid
        """
        self._ensure_connected()
        
        if not self.web3.is_address(address):
            raise ValueError(f"Invalid Ethereum address: {address}")
        
        return self.web3.eth.get_balance(address)
    
    def is_connected(self) -> bool:
        """
        Check if connected to an Ethereum network.
        
        Returns:
            bool: True if connected, False otherwise
        """
        if self.web3 is None:
            return False
        
        try:
            return self.web3.is_connected()
        except Exception:
            return False
    
    def create_transaction(
        self,
        to_address: str,
        value: int = 0,
        data: str = "",
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
        nonce: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Create a transaction object.
        
        Args:
            to_address: The recipient address
            value: The amount to send in wei
            data: The transaction data as hex string
            gas_limit: The gas limit
            gas_price: The gas price in wei
            nonce: The transaction nonce
            
        Returns:
            Dict[str, Any]: The transaction object
            
        Raises:
            ConnectionError: If not connected to a network
            ValueError: If parameters are invalid
        """
        self._ensure_connected()
        
        if not self.web3.is_address(to_address):
            raise ValueError(f"Invalid Ethereum address: {to_address}")
        
        transaction = {
            "to": to_address,
            "value": value,
            "chainId": self.web3.eth.chain_id,
        }
        
        if data:
            transaction["data"] = data if data.startswith("0x") else f"0x{data}"
        
        # Auto-fill gas limit if not provided
        if gas_limit is None:
            try:
                gas_limit = self.web3.eth.estimate_gas(transaction)
                # Add a buffer for safety
                gas_limit = int(gas_limit * 1.2)
            except Exception as e:
                raise TransactionError(f"Failed to estimate gas: {str(e)}")
        
        transaction["gas"] = gas_limit
        
        # Auto-fill gas price if not provided
        if gas_price is None:
            try:
                # Use EIP-1559 fee estimation if available
                fee_history = self.web3.eth.fee_history(1, 'latest', [50])
                base_fee = fee_history.base_fee_per_gas[0]
                priority_fee = fee_history.reward[0][0]
                transaction["maxFeePerGas"] = base_fee + priority_fee
                transaction["maxPriorityFeePerGas"] = priority_fee
            except Exception:
                # Fall back to legacy gas price
                transaction["gasPrice"] = self.web3.eth.gas_price
        else:
            transaction["gasPrice"] = gas_price
        
        # Auto-fill nonce if not provided
        if nonce is None:
            # This will require the from_address, which we don't have yet
            # Will be filled during signing
            pass
        else:
            transaction["nonce"] = nonce
        
        return transaction
    
    def sign_transaction(self, transaction: Dict[str, Any], private_key: str) -> str:
        """
        Sign a transaction.
        
        Args:
            transaction: The transaction object
            private_key: The private key to sign with
            
        Returns:
            str: The signed transaction as hex string
            
        Raises:
            ValueError: If the transaction or private key is invalid
        """
        self._ensure_connected()
        
        try:
            # Derive the address from the private key
            account = self.web3.eth.account.from_key(private_key)
            
            # Add from address
            transaction["from"] = account.address
            
            # Add nonce if not provided
            if "nonce" not in transaction:
                transaction["nonce"] = self.web3.eth.get_transaction_count(account.address)
            
            # Sign the transaction
            signed_tx = self.web3.eth.account.sign_transaction(transaction, private_key)
            
            return signed_tx.rawTransaction.hex()
        except Exception as e:
            raise ValueError(f"Failed to sign transaction: {str(e)}")
    
    def send_transaction(self, signed_transaction: str) -> str:
        """
        Send a signed transaction.
        
        Args:
            signed_transaction: The signed transaction as hex string
            
        Returns:
            str: The transaction hash
            
        Raises:
            ConnectionError: If not connected to a network
            ValueError: If the transaction is invalid
        """
        self._ensure_connected()
        
        try:
            # Convert to bytes if it's a hex string
            if isinstance(signed_transaction, str) and signed_transaction.startswith("0x"):
                signed_transaction = bytes.fromhex(signed_transaction[2:])
            
            # Send the transaction
            tx_hash = self.web3.eth.send_raw_transaction(signed_transaction)
            
            return tx_hash.hex()
        except Web3Exception as e:
            raise TransactionError(f"Failed to send transaction: {str(e)}")
    
    def get_transaction_receipt(self, transaction_hash: str) -> Optional[Dict[str, Any]]:
        """
        Get a transaction receipt.
        
        Args:
            transaction_hash: The transaction hash
            
        Returns:
            Optional[Dict[str, Any]]: The transaction receipt, or None if not found
            
        Raises:
            ConnectionError: If not connected to a network
        """
        self._ensure_connected()
        
        try:
            receipt = self.web3.eth.get_transaction_receipt(transaction_hash)
            if receipt is None:
                return None
            
            # Convert to a regular dict for better serialization
            return dict(receipt)
        except Web3Exception as e:
            if "not found" in str(e).lower():
                return None
            raise TransactionError(f"Failed to get transaction receipt: {str(e)}")
    
    def load_contract(self, address: str, abi: List[Dict[str, Any]]) -> Any:
        """
        Load a contract.
        
        Args:
            address: The contract address
            abi: The contract ABI
            
        Returns:
            Any: The contract object
            
        Raises:
            ConnectionError: If not connected to a network
            ValueError: If the address or ABI is invalid
        """
        self._ensure_connected()
        
        if not self.web3.is_address(address):
            raise ValueError(f"Invalid Ethereum address: {address}")
        
        try:
            contract = self.web3.eth.contract(address=address, abi=abi)
            return contract
        except Exception as e:
            raise ContractError(f"Failed to load contract: {str(e)}")
    
    def call_function(
        self, 
        contract: Any, 
        function_name: str, 
        args: List[Any] = None, 
        kwargs: Dict[str, Any] = None
    ) -> Any:
        """
        Call a contract function.
        
        Args:
            contract: The contract object
            function_name: The function name
            args: Positional arguments
            kwargs: Keyword arguments
            
        Returns:
            Any: The function result
            
        Raises:
            ConnectionError: If not connected to a network
            ValueError: If the function call is invalid
        """
        self._ensure_connected()
        
        if args is None:
            args = []
        
        if kwargs is None:
            kwargs = {}
        
        try:
            function = getattr(contract.functions, function_name)
            result = function(*args, **kwargs).call()
            return result
        except Exception as e:
            raise ContractError(f"Failed to call contract function: {str(e)}")
    
    def create_function_transaction(
        self, 
        contract: Any, 
        function_name: str, 
        args: List[Any] = None, 
        kwargs: Dict[str, Any] = None,
        value: int = 0,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Create a transaction for a contract function call.
        
        Args:
            contract: The contract object
            function_name: The function name
            args: Positional arguments
            kwargs: Keyword arguments
            value: The amount to send in wei
            gas_limit: The gas limit
            gas_price: The gas price in wei
            
        Returns:
            Dict[str, Any]: The transaction object
            
        Raises:
            ConnectionError: If not connected to a network
            ValueError: If the function call is invalid
        """
        self._ensure_connected()
        
        if args is None:
            args = []
        
        if kwargs is None:
            kwargs = {}
        
        try:
            function = getattr(contract.functions, function_name)
            transaction = function(*args, **kwargs).build_transaction({
                "chainId": self.web3.eth.chain_id,
                "value": value,
            })
            
            # Set gas limit if provided
            if gas_limit is not None:
                transaction["gas"] = gas_limit
            
            # Set gas price if provided
            if gas_price is not None:
                if "maxFeePerGas" in transaction:
                    # EIP-1559 transaction
                    del transaction["maxFeePerGas"]
                    del transaction["maxPriorityFeePerGas"]
                transaction["gasPrice"] = gas_price
            
            return transaction
        except Exception as e:
            raise ContractError(f"Failed to create contract function transaction: {str(e)}")
    
    def create_event_filter(
        self,
        contract: Any,
        event_name: str,
        from_block: Union[int, str] = "latest",
        to_block: Union[int, str] = "latest",
        argument_filters: Dict[str, Any] = None
    ) -> Any:
        """
        Create an event filter.
        
        Args:
            contract: The contract object
            event_name: The event name
            from_block: The starting block
            to_block: The ending block
            argument_filters: Filters for event arguments
            
        Returns:
            Any: The event filter object
            
        Raises:
            ConnectionError: If not connected to a network
            ValueError: If the event or filters are invalid
        """
        self._ensure_connected()
        
        if argument_filters is None:
            argument_filters = {}
        
        try:
            event = getattr(contract.events, event_name)
            event_filter = event.create_filter(
                fromBlock=from_block,
                toBlock=to_block,
                argument_filters=argument_filters
            )
            return event_filter
        except Exception as e:
            raise ContractError(f"Failed to create event filter: {str(e)}")
    
    def get_events(self, event_filter: Any) -> List[Dict[str, Any]]:
        """
        Get events from a filter.
        
        Args:
            event_filter: The event filter object
            
        Returns:
            List[Dict[str, Any]]: The events
            
        Raises:
            ConnectionError: If not connected to a network
        """
        self._ensure_connected()
        
        try:
            events = event_filter.get_all_entries()
            
            # Convert to a list of dicts for better serialization
            return [dict(event) for event in events]
        except Exception as e:
            raise ContractError(f"Failed to get events: {str(e)}")
    
    def subscribe_to_events(
        self,
        contract: Any,
        event_name: str,
        callback: callable,
        argument_filters: Dict[str, Any] = None
    ) -> Any:
        """
        Subscribe to events.
        
        Args:
            contract: The contract object
            event_name: The event name
            callback: The callback function to call for each event
            argument_filters: Filters for event arguments
            
        Returns:
            Any: The subscription object
            
        Raises:
            ConnectionError: If not connected to a network
            ValueError: If the event or filters are invalid
        """
        self._ensure_connected()
        
        # For HTTP provider, we can't do real-time subscriptions
        # So we need to poll for events
        # For WebSocket provider, we could use web3.eth.subscribe
        
        # This is a simplified implementation
        # In a real implementation, we would handle different provider types
        # and manage polling/subscriptions accordingly
        
        if argument_filters is None:
            argument_filters = {}
        
        try:
            event = getattr(contract.events, event_name)
            event_filter = event.create_filter(
                fromBlock="latest",
                argument_filters=argument_filters
            )
            
            # This isn't a real subscription, but a polling handler
            # In a real implementation, we would set up a polling loop
            # or use a real subscription for WebSocket providers
            
            return event_filter
        except Exception as e:
            raise ContractError(f"Failed to subscribe to events: {str(e)}")
    
    def _ensure_connected(self):
        """
        Ensure that the client is connected to a network.
        
        Raises:
            ConnectionError: If not connected to a network
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to an Ethereum network") 