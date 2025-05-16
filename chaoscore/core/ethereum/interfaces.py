"""
Ethereum Integration Interfaces

This module defines the interfaces for Ethereum blockchain interaction in the ChaosCore platform.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union


class BlockchainClient(ABC):
    """
    Interface for generic blockchain operations.
    """
    
    @abstractmethod
    def connect(self, endpoint_url: str) -> bool:
        """
        Connect to a blockchain network.
        
        Args:
            endpoint_url: The URL of the blockchain endpoint
            
        Returns:
            bool: True if connection was successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_chain_id(self) -> int:
        """
        Get the chain ID of the connected network.
        
        Returns:
            int: The chain ID
            
        Raises:
            ConnectionError: If not connected to a network
        """
        pass
    
    @abstractmethod
    def get_latest_block_number(self) -> int:
        """
        Get the latest block number.
        
        Returns:
            int: The latest block number
            
        Raises:
            ConnectionError: If not connected to a network
        """
        pass
    
    @abstractmethod
    def get_balance(self, address: str) -> int:
        """
        Get the balance of an address.
        
        Args:
            address: The address to check
            
        Returns:
            int: The balance in wei
            
        Raises:
            ConnectionError: If not connected to a network
            ValueError: If the address is invalid
        """
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """
        Check if connected to a blockchain network.
        
        Returns:
            bool: True if connected, False otherwise
        """
        pass


class TransactionManager(ABC):
    """
    Interface for transaction creation and submission.
    """
    
    @abstractmethod
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
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
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
        pass


class ContractInteraction(ABC):
    """
    Interface for smart contract interaction.
    """
    
    @abstractmethod
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
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
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
        pass


class EventMonitor(ABC):
    """
    Interface for event subscription and processing.
    """
    
    @abstractmethod
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
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
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
        pass


class BlockchainIntegrationError(Exception):
    """Base class for blockchain integration errors."""
    pass


class ConnectionError(BlockchainIntegrationError):
    """Error raised when connection to the blockchain fails."""
    pass


class TransactionError(BlockchainIntegrationError):
    """Error raised when a transaction fails."""
    pass


class ContractError(BlockchainIntegrationError):
    """Error raised when contract interaction fails."""
    pass 