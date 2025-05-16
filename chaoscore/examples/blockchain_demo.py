#!/usr/bin/env python
"""
Ethereum Client Demonstration Script

This script demonstrates the basic functionality of the Ethereum client:
1. Connecting to an Ethereum network (Goerli testnet or local fork)
2. Getting basic blockchain information
3. Creating and signing a transaction
4. Working with smart contracts

Usage:
    python blockchain_demo.py [--local]

Arguments:
    --local: Use a local Anvil fork instead of connecting to Goerli
"""
import os
import sys
import argparse
import json
from web3 import Web3

# Add the root directory to the Python path to access the chaoscore module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from chaoscore.core.ethereum.implementation import EthereumClient
from chaoscore.core.ethereum.interfaces import ConnectionError, TransactionError, ContractError


def main():
    parser = argparse.ArgumentParser(description="Ethereum Client Demo")
    parser.add_argument("--local", action="store_true", help="Use local Anvil fork instead of Goerli")
    args = parser.parse_args()
    
    # Initialize the Ethereum client
    client = EthereumClient()
    
    # Endpoint URL
    if args.local:
        endpoint_url = "http://localhost:8545"  # Anvil default
        print(f"Using local Anvil fork at {endpoint_url}")
    else:
        # For Goerli, we need an endpoint URL
        # You can get one from Infura, Alchemy, etc.
        endpoint_url = os.environ.get("ETHEREUM_ENDPOINT_URL")
        if not endpoint_url:
            print("Error: ETHEREUM_ENDPOINT_URL environment variable not set.")
            print("Please set it to a valid Ethereum node URL (e.g., Infura, Alchemy)")
            print("Example: export ETHEREUM_ENDPOINT_URL=https://goerli.infura.io/v3/your-api-key")
            sys.exit(1)
        print(f"Using Goerli testnet at {endpoint_url}")
    
    try:
        # Connect to the Ethereum network
        print("\nConnecting to Ethereum network...")
        connected = client.connect(endpoint_url)
        if not connected:
            print("Failed to connect to Ethereum network.")
            sys.exit(1)
        print("Successfully connected to Ethereum network.")
        
        # Get basic blockchain information
        print("\nFetching blockchain information...")
        chain_id = client.get_chain_id()
        block_number = client.get_latest_block_number()
        
        print(f"Chain ID: {chain_id}")
        print(f"Latest Block Number: {block_number}")
        
        # Get test account information
        # For a local Anvil fork, we can use the built-in accounts
        # For Goerli, we need to provide a valid account
        if args.local:
            # Anvil provides accounts with test ETH
            w3 = Web3(Web3.HTTPProvider(endpoint_url))
            accounts = w3.eth.accounts
            from_address = accounts[0]
            to_address = accounts[1]
            
            # Get the balance of the from_address
            balance = client.get_balance(from_address)
            print(f"\nAccount: {from_address}")
            print(f"Balance: {Web3.from_wei(balance, 'ether')} ETH")
            
            # Create a transaction
            print("\nCreating a transaction...")
            tx = client.create_transaction(
                to_address=to_address,
                value=Web3.to_wei(0.01, 'ether'),
                gas_limit=21000,
                gas_price=Web3.to_wei(20, 'gwei')
            )
            print(f"Transaction created: {json.dumps(tx, indent=2)}")
            
            # Sign and send the transaction
            # We need the private key for the from_address
            # In Anvil, we can get it from the accounts
            # In a real scenario, NEVER hardcode private keys
            private_key = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"  # First Anvil test account private key
            
            print("\nSigning the transaction...")
            signed_tx = client.sign_transaction(tx, private_key)
            print(f"Transaction signed.")
            
            print("\nSending the transaction...")
            tx_hash = client.send_transaction(signed_tx)
            print(f"Transaction sent. Hash: {tx_hash}")
            
            # Wait for the transaction to be mined
            print("\nWaiting for transaction receipt...")
            receipt = None
            while receipt is None:
                receipt = client.get_transaction_receipt(tx_hash)
            
            print(f"Transaction mined in block {receipt['blockNumber']}")
            print(f"Gas used: {receipt['gasUsed']}")
            print(f"Status: {'Success' if receipt['status'] == 1 else 'Failed'}")
        
        else:
            print("\nTo perform transactions on Goerli testnet, you need to provide:")
            print("1. A valid Ethereum account with ETH")
            print("2. The private key for the account (which should be kept secret)")
            print("\nFor security reasons, we don't demonstrate this in the script.")
            print("You can modify the script to use your own account and private key.")
        
        # Demonstrate contract interaction (using a mock for this example)
        print("\nContract interaction demonstration:")
        print("This would involve:")
        print("1. Loading a contract using its ABI and address")
        print("2. Calling read functions to get data")
        print("3. Creating transactions for write functions")
        print("4. Signing and sending those transactions")
        print("5. Listening for events emitted by the contract")
        
    except ConnectionError as e:
        print(f"Connection error: {str(e)}")
    except TransactionError as e:
        print(f"Transaction error: {str(e)}")
    except ContractError as e:
        print(f"Contract error: {str(e)}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
    finally:
        print("\nDemo completed.")


if __name__ == "__main__":
    main() 