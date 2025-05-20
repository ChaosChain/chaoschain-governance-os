"""
Ethereum Client for ChaosCore

This module provides a client for interacting with Ethereum blockchain
and the ChaosEndpoint contract.
"""
import os
import json
import logging
from typing import Dict, Any, Optional, List, Tuple
from hexbytes import HexBytes

from web3 import Web3
from eth_account import Account

# Set up logging
logger = logging.getLogger(__name__)

# Try to import geth_poa_middleware, but don't fail if it's not available
try:
    from web3.middleware import geth_poa_middleware
    HAS_POA_MIDDLEWARE = True
except ImportError:
    logger.warning("geth_poa_middleware not available in web3 library. POA chains may not work correctly.")
    HAS_POA_MIDDLEWARE = False


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
        from pathlib import Path, PurePath
        import json

        self.rpc_url = rpc_url or os.environ.get('ETHEREUM_PROVIDER_URL')
        self.private_key = private_key or os.environ.get('ETHEREUM_PRIVATE_KEY')
        self.mock_mode = os.environ.get('ETHEREUM_MOCK', 'false').lower() == 'true'
        
        # Try to load address and ABI from artifact file
        try:
            artifact_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'deployments', 'sepolia', 'ChaosEndpoint.json')
            abi_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', 'deployments', 'sepolia', 'ChaosEndpoint.abi.json')
            
            # Load contract address from artifact
            if os.path.exists(artifact_path):
                with open(artifact_path) as f:
                    info = json.load(f)
                    self.contract_address = info.get("address")
                    logger.info(f"Loaded contract address from artifact: {self.contract_address}")
            
            # If no address from artifact, use environment variable
            if not self.contract_address:
                self.contract_address = contract_address or os.environ.get('ETHEREUM_CONTRACT_ADDRESS')
        except Exception as e:
            logger.warning(f"Failed to load contract address from artifact: {e}")
            self.contract_address = contract_address or os.environ.get('ETHEREUM_CONTRACT_ADDRESS')
        
        # Ensure private key has 0x prefix
        if self.private_key and not self.private_key.startswith('0x'):
            self.private_key = f"0x{self.private_key}"
        
        logger.info(f"Initializing Ethereum client with RPC URL: {self.rpc_url}")
        logger.info(f"Contract address: {self.contract_address}")
        logger.info(f"Mock mode: {self.mock_mode}")
        
        # Initialize web3.py client
        # Use a retry_middleware to handle temporary network issues
        self.w3 = None
        if self.rpc_url:
            try:
                self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
                
                # Configure for PoA networks
                if HAS_POA_MIDDLEWARE:
                    self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
                
                # Set up default account
                if self.private_key:
                    account = self.w3.eth.account.from_key(self.private_key)
                    self.w3.eth.default_account = account.address
                
                logger.info(f"Connected to Ethereum network: {self.is_connected()}")
            except Exception as e:
                logger.error(f"Failed to connect to Ethereum network: {e}")
                self.w3 = None
        
        # Load contract ABI from CHAOS_ENDPOINT_ABI environment variable first
        chaos_endpoint_abi_path = os.environ.get('CHAOS_ENDPOINT_ABI')
        if chaos_endpoint_abi_path:
            try:
                logger.info(f"Loading ABI from CHAOS_ENDPOINT_ABI path: {chaos_endpoint_abi_path}")
                if not os.path.exists(chaos_endpoint_abi_path):
                    raise FileNotFoundError(f"ABI file not found: {chaos_endpoint_abi_path}")
                
                with open(chaos_endpoint_abi_path, 'r') as f:
                    self.contract_abi = json.load(f)
                logger.info(f"ABI loaded successfully from {chaos_endpoint_abi_path}")
            except Exception as e:
                logger.error(f"Failed to load ABI from {chaos_endpoint_abi_path}: {e}")
                raise  # Fail fast if ABI file is missing
        # Fall back to provided contract_abi_path
        elif contract_abi_path:
            with open(contract_abi_path, 'r') as f:
                contract_json = json.load(f)
                # Handle different ABI formats
                if 'abi' in contract_json:
                    self.contract_abi = contract_json['abi']
                else:
                    self.contract_abi = contract_json
        else:
            # Try to load ABI from the mounted artifact file
            try:
                if os.path.exists(abi_path):
                    with open(abi_path, 'r') as f:
                        abi_json = json.load(f)
                        if 'abi' in abi_json:
                            self.contract_abi = abi_json['abi']
                        else:
                            self.contract_abi = abi_json
                    logger.info(f"ABI loaded successfully from {abi_path}")
                else:
                    # Check for environment variable
                    abi_path_env = os.environ.get('ETHEREUM_ABI_PATH')
                    if abi_path_env and os.path.exists(abi_path_env):
                        try:
                            logger.info(f"Loading ABI from environment variable path: {abi_path_env}")
                            with open(abi_path_env, 'r') as f:
                                contract_json = json.load(f)
                                # Handle different ABI formats
                                if 'abi' in contract_json:
                                    self.contract_abi = contract_json['abi']
                                else:
                                    self.contract_abi = contract_json
                            logger.info(f"ABI loaded successfully from {abi_path_env}")
                        except Exception as e:
                            logger.error(f"Failed to load ABI from {abi_path_env}: {e}")
                            self.contract_abi = None
                    else:
                        # Fallback to default Hardhat artifact location
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
            except Exception as e:
                logger.error(f"Failed to load ABI from artifact: {e}")
                raise  # Fail fast if ABI can't be loaded
        
        # Set up contract instance
        if self.contract_address and self.w3:
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

    def anchor_proof(self, proof_hash: str, agent_id: str = None) -> Tuple[str, int]:
        """
        Anchor a proof hash to the blockchain using the ChaosEndpoint.anchorAction function.
        
        Args:
            proof_hash: The hash to anchor (bytes32)
            agent_id: The ID of the agent that is performing the action (must be registered)
            
        Returns:
            Tuple[str, int]: Transaction hash (hex) and block number
            
        Raises:
            Exception: If the contract is not configured or the transaction fails
        """
        if not self.contract:
            raise Exception("Contract not configured")
        
        if not self.private_key:
            raise Exception("No private key configured for transaction signing")
        
        # Get account from private key
        account = self.w3.eth.account.from_key(self.private_key)
        address = account.address
        
        # Get nonce for address
        nonce = self.w3.eth.get_transaction_count(address)
        
        # Convert parameters to appropriate format
        # Note: for anchorAction, we need:
        # - action_id (string)
        # - agent_id (string)
        # - action_type (string)
        # - metadata_uri (string)
        # - attestation (bytes memory)

        # For action_id, use the proof hash directly
        if not proof_hash.startswith('0x'):
            action_id = '0x' + proof_hash
        else:
            action_id = proof_hash
            
        # If no agent_id was provided, generate one
        if not agent_id:
            agent_id = f"agent-{proof_hash[:8]}"
            
        action_type = "ANCHOR"
        metadata_uri = ""
        attestation = b''  # Empty bytes
        
        logger.info(f"Anchoring action to blockchain with hash: {action_id}")
        logger.info(f"Using agent_id: {agent_id}")
        
        try:
            # Create the transaction function to call - using string arguments as required by ABI
            tx_func = self.contract.functions.anchorAction(
                action_id,  # string
                agent_id,   # string
                action_type,  # string
                metadata_uri,  # string
                attestation  # bytes
            )
            
            # Estimate gas for the transaction
            try:
                estimated_gas = tx_func.estimateGas({'from': address}) * 2  # Double the estimated gas to be safe
                logger.info(f"Estimated gas for transaction: {estimated_gas}")
            except Exception as e:
                logger.warning(f"Gas estimation failed: {e}. Using default gas limit of 500,000")
                estimated_gas = 500000
            
            # Build transaction with estimated gas
            tx = tx_func.build_transaction({
                "from": address,
                "nonce": nonce,
                "gas": int(estimated_gas),
                "gasPrice": self.w3.eth.gas_price * 2,  # Double the gas price for faster confirmation
            })
            
            # Sign and send transaction
            signed_tx = self.w3.eth.account.sign_transaction(tx, self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            
            logger.info(f"Transaction sent with hash: {tx_hash.hex()}")
            
            # Wait for transaction receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
            
            # Check transaction status
            if receipt.status != 1:
                # Try to get revert reason
                try:
                    # Re-execute the tx locally to get revert reason
                    self.w3.eth.call(dict(tx, gasPrice=0), receipt.blockNumber)
                except Exception as e:
                    revert_msg = str(e)
                    logger.error(f"Transaction reverted with reason: {revert_msg}")
                    raise RuntimeError(f"Anchor transaction reverted: {revert_msg}")
                
                raise RuntimeError("Anchor transaction reverted with unknown reason")
            
            logger.info(f"Transaction confirmed in block {receipt.blockNumber}")
            
            # Return transaction hash (hex) and block number
            return (tx_hash.hex(), receipt.blockNumber)
            
        except Exception as e:
            logger.error(f"Failed to anchor action: {str(e)}")
            raise Exception(f"Failed to anchor action: {str(e)}")
    
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
        
        logger.info(f"Registering agent {agent_id} with metadata_uri {metadata_uri}")
        
        try:
            # Create the transaction function to call
            tx_func = self.contract.functions.registerAgent(
                agent_id,
                metadata_uri,
                attestation
            )
            
            # Estimate gas for the transaction
            try:
                estimated_gas = tx_func.estimateGas({'from': address}) * 2  # Double the estimated gas to be safe
                logger.info(f"Estimated gas for transaction: {estimated_gas}")
            except Exception as e:
                logger.warning(f"Gas estimation failed: {e}. Using default gas limit of 500,000")
                estimated_gas = 500000
            
            # Build transaction with estimated gas
            tx = tx_func.build_transaction({
                'from': address,
                'nonce': self.w3.eth.get_transaction_count(address),
                'gas': int(estimated_gas),
                'gasPrice': self.w3.eth.gas_price * 2  # Double gas price for faster confirmation
            })
            
            # Sign and send transaction
            signed_tx = self.w3.eth.account.sign_transaction(tx, self.private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            
            logger.info(f"Transaction sent with hash: {tx_hash.hex()}")
            
            # Wait for transaction receipt
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            # Check transaction status
            if tx_receipt.status != 1:
                # Try to get revert reason
                try:
                    # Re-execute the tx locally to get revert reason
                    self.w3.eth.call(dict(tx, gasPrice=0), tx_receipt.blockNumber)
                except Exception as e:
                    revert_msg = str(e)
                    logger.error(f"Transaction reverted with reason: {revert_msg}")
                    raise RuntimeError(f"Register agent transaction reverted: {revert_msg}")
                
                raise RuntimeError("Register agent transaction reverted with unknown reason")
            
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
            
        except Exception as e:
            logger.error(f"Failed to register agent: {str(e)}")
            raise Exception(f"Failed to register agent: {str(e)}")
    
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
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
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
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
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
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
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
        
        logger.info(f"Checking if agent {agent_id} is registered")
        
        try:
            # Call the isAgentRegistered function on the contract
            return self.contract.functions.isAgentRegistered(agent_id).call()
        except Exception as e:
            logger.error(f"Error checking if agent {agent_id} is registered: {str(e)}")
            return False
    
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