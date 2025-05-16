"""
Ethereum Client for ChaosCore

This module provides a client for interacting with Ethereum blockchain
and the ChaosEndpoint contract.
"""
import os
import json
from typing import Dict, Any, Optional, List

from web3 import Web3
from web3.middleware import geth_poa_middleware


class EthereumClient:
    """
    Client for interacting with Ethereum blockchain and the ChaosEndpoint contract.
    """
    
    def __init__(
        self,
        rpc_url: Optional[str] = None,
        contract_address: Optional[str] = None,
        private_key: Optional[str] = None,
        contract_abi_path: Optional[str] = None
    ):
        """
        Initialize the Ethereum client.
        
        Args:
            rpc_url: The URL of the Ethereum RPC endpoint (default: environment variable)
            contract_address: The address of the ChaosEndpoint contract (default: environment variable)
            private_key: The private key to use for signing transactions (default: environment variable)
            contract_abi_path: The path to the contract ABI JSON file (default: built-in path)
        """
        # Get configuration from environment variables if not provided
        self.rpc_url = rpc_url or os.environ.get('ETHEREUM_RPC_URL', 'http://localhost:8545')
        self.contract_address = contract_address or os.environ.get('CHAOS_CONTRACT_ADDRESS')
        self.private_key = private_key or os.environ.get('ETHEREUM_PRIVATE_KEY')
        
        # Set up web3 connection
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        
        # Add middleware for POA chains (e.g., Goerli, Sepolia)
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        
        # Load contract ABI
        if contract_abi_path:
            with open(contract_abi_path, 'r') as f:
                self.contract_abi = json.load(f)
        else:
            # Default ABI path
            default_abi_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                '..', '..', '..', 'ethereum', 'artifacts', 'contracts', 'ChaosEndpoint.sol', 'ChaosEndpoint.json'
            )
            try:
                with open(default_abi_path, 'r') as f:
                    contract_json = json.load(f)
                    self.contract_abi = contract_json['abi']
            except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
                raise Exception(f"Failed to load contract ABI: {str(e)}")
        
        # Set up contract instance
        if self.contract_address:
            self.contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(self.contract_address),
                abi=self.contract_abi
            )
        else:
            self.contract = None
    
    def is_connected(self) -> bool:
        """
        Check if the client is connected to the Ethereum network.
        
        Returns:
            bool: True if connected, False otherwise
        """
        return self.w3.is_connected()
    
    def get_account(self) -> str:
        """
        Get the account address derived from the private key.
        
        Returns:
            str: The account address
        
        Raises:
            Exception: If no private key is configured
        """
        if not self.private_key:
            raise Exception("No private key configured")
        
        account = self.w3.eth.account.from_key(self.private_key)
        return account.address
    
    def register_agent(
        self,
        agent_id: str,
        metadata_uri: str,
        attestation: bytes
    ) -> Dict[str, Any]:
        """
        Register an agent on the blockchain.
        
        Args:
            agent_id: The unique identifier for the agent
            metadata_uri: IPFS or HTTP URI containing agent metadata
            attestation: TEE attestation proving the agent's integrity
            
        Returns:
            Dict[str, Any]: Transaction details including hash and receipt
            
        Raises:
            Exception: If the contract is not configured or the transaction fails
        """
        if not self.contract:
            raise Exception("Contract not configured")
        
        if not self.private_key:
            raise Exception("No private key configured")
        
        # Get account from private key
        account = self.w3.eth.account.from_key(self.private_key)
        address = account.address
        
        # Build transaction
        tx = self.contract.functions.registerAgent(
            agent_id,
            metadata_uri,
            attestation
        ).build_transaction({
            'from': address,
            'nonce': self.w3.eth.get_transaction_count(address),
            'gas': 500000,
            'gasPrice': self.w3.eth.gas_price
        })
        
        # Sign and send transaction
        signed_tx = self.w3.eth.account.sign_transaction(tx, self.private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        # Wait for transaction receipt
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        
        # Process logs to extract event data
        logs = []
        for log in tx_receipt.logs:
            try:
                decoded_log = self.contract.events.AgentRegistered().process_log(log)
                logs.append(decoded_log)
            except:
                pass
        
        return {
            'hash': tx_hash.hex(),
            'receipt': dict(tx_receipt),
            'events': logs
        }
    
    def anchor_action(
        self,
        action_id: str,
        agent_id: str,
        action_type: str,
        metadata_uri: str,
        attestation: bytes
    ) -> Dict[str, Any]:
        """
        Anchor an action on the blockchain.
        
        Args:
            action_id: The unique identifier for the action
            agent_id: The ID of the agent that performed the action
            action_type: The type of the action (e.g., ANALYZE, CREATE)
            metadata_uri: IPFS or HTTP URI containing action metadata
            attestation: TEE attestation proving the action's integrity
            
        Returns:
            Dict[str, Any]: Transaction details including hash and receipt
            
        Raises:
            Exception: If the contract is not configured or the transaction fails
        """
        if not self.contract:
            raise Exception("Contract not configured")
        
        if not self.private_key:
            raise Exception("No private key configured")
        
        # Get account from private key
        account = self.w3.eth.account.from_key(self.private_key)
        address = account.address
        
        # Build transaction
        tx = self.contract.functions.anchorAction(
            action_id,
            agent_id,
            action_type,
            metadata_uri,
            attestation
        ).build_transaction({
            'from': address,
            'nonce': self.w3.eth.get_transaction_count(address),
            'gas': 500000,
            'gasPrice': self.w3.eth.gas_price
        })
        
        # Sign and send transaction
        signed_tx = self.w3.eth.account.sign_transaction(tx, self.private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        # Wait for transaction receipt
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        
        # Process logs to extract event data
        logs = []
        for log in tx_receipt.logs:
            try:
                decoded_log = self.contract.events.ActionAnchored().process_log(log)
                logs.append(decoded_log)
            except:
                pass
        
        return {
            'hash': tx_hash.hex(),
            'receipt': dict(tx_receipt),
            'events': logs
        }
    
    def record_outcome(
        self,
        action_id: str,
        outcome_uri: str
    ) -> Dict[str, Any]:
        """
        Record an outcome for an anchored action.
        
        Args:
            action_id: The ID of the anchored action
            outcome_uri: IPFS or HTTP URI containing outcome metadata
            
        Returns:
            Dict[str, Any]: Transaction details including hash and receipt
            
        Raises:
            Exception: If the contract is not configured or the transaction fails
        """
        if not self.contract:
            raise Exception("Contract not configured")
        
        if not self.private_key:
            raise Exception("No private key configured")
        
        # Get account from private key
        account = self.w3.eth.account.from_key(self.private_key)
        address = account.address
        
        # Build transaction
        tx = self.contract.functions.recordOutcome(
            action_id,
            outcome_uri
        ).build_transaction({
            'from': address,
            'nonce': self.w3.eth.get_transaction_count(address),
            'gas': 300000,
            'gasPrice': self.w3.eth.gas_price
        })
        
        # Sign and send transaction
        signed_tx = self.w3.eth.account.sign_transaction(tx, self.private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        # Wait for transaction receipt
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        
        return {
            'hash': tx_hash.hex(),
            'receipt': dict(tx_receipt)
        }
    
    def distribute_rewards(
        self,
        action_id: str,
        recipients_data: str
    ) -> Dict[str, Any]:
        """
        Distribute rewards for an action.
        
        Args:
            action_id: The ID of the anchored action
            recipients_data: JSON string containing recipient addresses and amounts
            
        Returns:
            Dict[str, Any]: Transaction details including hash and receipt
            
        Raises:
            Exception: If the contract is not configured or the transaction fails
        """
        if not self.contract:
            raise Exception("Contract not configured")
        
        if not self.private_key:
            raise Exception("No private key configured")
        
        # Get account from private key
        account = self.w3.eth.account.from_key(self.private_key)
        address = account.address
        
        # Build transaction
        tx = self.contract.functions.distributeRewards(
            action_id,
            recipients_data
        ).build_transaction({
            'from': address,
            'nonce': self.w3.eth.get_transaction_count(address),
            'gas': 300000,
            'gasPrice': self.w3.eth.gas_price
        })
        
        # Sign and send transaction
        signed_tx = self.w3.eth.account.sign_transaction(tx, self.private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        # Wait for transaction receipt
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        
        # Process logs to extract event data
        logs = []
        for log in tx_receipt.logs:
            try:
                decoded_log = self.contract.events.RewardsDistributed().process_log(log)
                logs.append(decoded_log)
            except:
                pass
        
        return {
            'hash': tx_hash.hex(),
            'receipt': dict(tx_receipt),
            'events': logs
        }
    
    def is_agent_registered(self, agent_id: str) -> bool:
        """
        Check if an agent is registered.
        
        Args:
            agent_id: The ID of the agent to check
            
        Returns:
            bool: Whether the agent is registered
            
        Raises:
            Exception: If the contract is not configured
        """
        if not self.contract:
            raise Exception("Contract not configured")
        
        return self.contract.functions.isAgentRegistered(agent_id).call()
    
    def is_action_anchored(self, action_id: str) -> bool:
        """
        Check if an action is anchored.
        
        Args:
            action_id: The ID of the action to check
            
        Returns:
            bool: Whether the action is anchored
            
        Raises:
            Exception: If the contract is not configured
        """
        if not self.contract:
            raise Exception("Contract not configured")
        
        return self.contract.functions.isActionAnchored(action_id).call()
    
    def get_agent_registration(self, agent_id: str) -> Dict[str, Any]:
        """
        Get agent registration details.
        
        Args:
            agent_id: The ID of the agent to retrieve
            
        Returns:
            Dict[str, Any]: The agent registration details
            
        Raises:
            Exception: If the contract is not configured or the agent is not registered
        """
        if not self.contract:
            raise Exception("Contract not configured")
        
        if not self.is_agent_registered(agent_id):
            raise Exception(f"Agent {agent_id} not registered")
        
        registration = self.contract.functions.getAgentRegistration(agent_id).call()
        
        return {
            'agent_id': registration[0],
            'registrar': registration[1],
            'metadata_uri': registration[2],
            'attestation': registration[3],
            'timestamp': registration[4]
        }
    
    def get_anchored_action(self, action_id: str) -> Dict[str, Any]:
        """
        Get anchored action details.
        
        Args:
            action_id: The ID of the action to retrieve
            
        Returns:
            Dict[str, Any]: The anchored action details
            
        Raises:
            Exception: If the contract is not configured or the action is not anchored
        """
        if not self.contract:
            raise Exception("Contract not configured")
        
        if not self.is_action_anchored(action_id):
            raise Exception(f"Action {action_id} not anchored")
        
        action = self.contract.functions.getAnchoredAction(action_id).call()
        
        return {
            'action_id': action[0],
            'agent_id': action[1],
            'action_type': action[2],
            'metadata_uri': action[3],
            'attestation': action[4],
            'timestamp': action[5],
            'has_outcome': action[6],
            'outcome_uri': action[7]
        } 