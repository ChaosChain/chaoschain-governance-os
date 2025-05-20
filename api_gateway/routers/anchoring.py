"""
Anchoring Router

This module provides the API router for anchoring operations on Ethereum.
"""

import os
import logging
import hashlib
import time
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

from fastapi import APIRouter, HTTPException, Depends, status

from api_gateway.dependencies import get_db_adapter
from api_gateway.auth.jwt_auth import get_current_agent_id
from chaoscore.core.ethereum.client import EthereumClient

# Set up logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Ethereum client setup
RPC_URL = os.getenv("ETHEREUM_PROVIDER_URL")
CONTRACT_ADDRESS = os.getenv("ETHEREUM_CONTRACT_ADDRESS")
PRIVATE_KEY = os.getenv("ETHEREUM_PRIVATE_KEY")

# Check if Ethereum mock mode is enabled
ETHEREUM_MOCK = os.getenv("ETHEREUM_MOCK", "false").lower() == "true"

if not ETHEREUM_MOCK:
    # Only initialize the client if not in mock mode
    try:
        if not PRIVATE_KEY:
            logger.error("ETHEREUM_PRIVATE_KEY not set, cannot send real transactions!")
            eth_client = None
        else:
            eth_client = EthereumClient(
                rpc_url=RPC_URL,
                contract_address=CONTRACT_ADDRESS,
                private_key=PRIVATE_KEY
            )
            logger.info(f"Ethereum client initialized with contract at {CONTRACT_ADDRESS}")
    except Exception as e:
        logger.error(f"Failed to initialize Ethereum client: {e}")
        eth_client = None
else:
    logger.warning("ETHEREUM_MOCK=true - Using mock transactions instead of real ones")
    eth_client = None


# --- Models ---

class AnchoringRequest(BaseModel):
    """
    Request to anchor an action to a blockchain.
    """
    action_id: str = Field(..., description="ID of the action to anchor")
    network: Optional[str] = Field("sepolia", description="Blockchain network to use (default: sepolia)")


class AnchorResponse(BaseModel):
    """Anchor response model."""
    tx_hash: str = Field(..., description="Transaction hash")
    action_id: str = Field(..., description="Action ID")
    network: str = Field(..., description="Ethereum network")
    block_number: Optional[int] = Field(None, description="Block number")
    status: str = Field(..., description="Transaction status")


# --- Routes ---

@router.post("/anchor", response_model=dict)
@router.post("", response_model=dict)  # Also handle the root path for backward compatibility
async def anchor_action(
    anchor_request: AnchoringRequest,
    db=Depends(get_db_adapter),
    current_agent_id: str = Depends(get_current_agent_id),
):
    """
    Anchor an action proof to the blockchain.
    
    This endpoint takes an action ID and anchors a proof of it to the blockchain,
    returning the transaction hash for verification.
    
    Args:
        anchor_request: The request containing the action ID
        db: The database adapter
        current_agent_id: The authenticated agent ID
        
    Returns:
        dict: The transaction hash and block number
    """
    try:
        action_id = anchor_request.action_id
        network = anchor_request.network or "sepolia"  # Default to Sepolia testnet
        
        logger.info(f"Anchoring action {action_id} to {network} blockchain")
        
        # Get the action from the database
        action = db.get_action(action_id)
        if not action:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Action with ID {action_id} not found"
            )
        
        # Get the agent who performed the action
        agent_id = action.get("agent_id")
        if not agent_id:
            agent_id = current_agent_id
        
        # Generate proof hash from action ID
        # In a production system, this would be a cryptographic proof of the action
        # For now, we'll use a simple SHA-256 hash of the action ID
        proof_hash = hashlib.sha256(action_id.encode()).hexdigest()
        
        # Check if ETHEREUM_MOCK is true or eth_client is not initialized
        if os.environ.get("ETHEREUM_MOCK", "true").lower() == "true" or eth_client is None:
            logger.warning(f"Using mock transaction for action {action_id} (ETHEREUM_MOCK={os.environ.get('ETHEREUM_MOCK', 'true')})")
            # Return mock transaction hash
            return {
                "tx_hash": f"0x{hashlib.sha256(f'{action_id}-{network}'.encode()).hexdigest()}",
                "block_number": 12345678,
                "network": network,
                "is_mock": True,
                "action_id": action_id,
            }
        
        # Use the Ethereum client to anchor the proof
        try:
            # First, check if the agent is registered
            try:
                is_registered = eth_client.is_agent_registered(agent_id)
                logger.info(f"Agent {agent_id} registration status: {is_registered}")
                
                # If agent is not registered, register it first
                if not is_registered:
                    logger.info(f"Registering agent {agent_id} on the blockchain")
                    # Get the agent details from the database
                    agent = db.get_agent(agent_id)
                    if not agent:
                        raise Exception(f"Agent {agent_id} not found in database")
                    
                    # Generate metadata URI (e.g., JSON string with agent info)
                    metadata_uri = f"https://chaoscore.io/agents/{agent_id}"
                    
                    # Register the agent
                    reg_result = eth_client.register_agent(
                        agent_id=agent_id,
                        metadata_uri=metadata_uri,
                        attestation=b''  # Empty attestation for now
                    )
                    
                    logger.info(f"Agent {agent_id} registered with transaction hash: {reg_result['hash']}")
                    
                    # Wait a bit to ensure the transaction is mined
                    logger.info("Waiting for agent registration to be confirmed...")
                    for _ in range(5):
                        is_registered = eth_client.is_agent_registered(agent_id)
                        if is_registered:
                            logger.info(f"Agent {agent_id} confirmed as registered")
                            break
                        time.sleep(2)  # Wait 2 seconds
                    
                    if not is_registered:
                        logger.warning(f"Agent {agent_id} registration not confirmed after waiting, proceeding anyway")
            except Exception as e:
                logger.error(f"Error checking/registering agent: {str(e)}")
                # Continue anyway, the actual anchor might still work
            
            # Now try to anchor the action
            logger.info(f"Sending transaction to blockchain with proof hash: {proof_hash}")
            tx_hash, block_number = eth_client.anchor_proof(proof_hash, agent_id=agent_id)
            
            # Store the transaction details in the database
            db.update_action_anchoring(
                action_id=action_id,
                tx_hash=tx_hash,
                network=network,
                block_number=block_number
            )
            
            logger.info(f"Successfully anchored action {action_id} with transaction hash {tx_hash}")
            
            # Return the transaction hash and block number
            return {
                "tx_hash": tx_hash,
                "block_number": block_number,
                "network": network,
                "is_mock": False,
                "action_id": action_id,
                "status": "confirmed"
            }
        except Exception as e:
            logger.error(f"Ethereum transaction failed: {str(e)}")
            # Re-raise as HTTP exception
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to anchor action: {str(e)}"
            )
        
    except HTTPException:
        # Re-raise HTTP exceptions directly
        raise
    except Exception as e:
        logger.error(f"Failed to anchor action {anchor_request.action_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to anchor action: {str(e)}"
        ) 