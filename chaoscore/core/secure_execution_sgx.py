"""
Secure Execution Environment using SGX

This module provides a Secure Execution Environment implementation using Intel SGX.
"""
import os
import json
import logging
import base64
import hashlib
import requests
from typing import Dict, Any, Callable
import pickle
import dill

logger = logging.getLogger(__name__)


class SGXSecureExecutionEnvironment:
    """
    SGX-based Secure Execution Environment.
    """
    
    def __init__(self, enclave_url=None):
        """
        Initialize the SGX-based Secure Execution Environment.
        
        Args:
            enclave_url: URL of the SGX enclave service
        """
        self.enclave_url = enclave_url or os.environ.get("SGX_ENCLAVE_URL", "http://localhost:7000")
        
    def run(self, func, *args, **kwargs) -> Dict[str, Any]:
        """
        Run a function in the secure execution environment.
        
        Args:
            func: Function to run
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Dictionary with result and attestation
        """
        # Serialize the function and arguments
        try:
            serialized_func = dill.dumps(func)
            serialized_args = pickle.dumps(args)
            serialized_kwargs = pickle.dumps(kwargs)
            
            # Encode for transmission
            encoded_func = base64.b64encode(serialized_func).decode('utf-8')
            encoded_args = base64.b64encode(serialized_args).decode('utf-8')
            encoded_kwargs = base64.b64encode(serialized_kwargs).decode('utf-8')
            
            # Prepare the request payload
            payload = {
                "function": encoded_func,
                "args": encoded_args,
                "kwargs": encoded_kwargs
            }
            
            # Send the request to the SGX enclave
            response = requests.post(f"{self.enclave_url}/execute", json=payload)
            
            if response.status_code != 200:
                logger.error(f"SGX execution failed: {response.text}")
                raise Exception(f"SGX execution failed: {response.text}")
            
            result_data = response.json()
            
            # Extract the result and attestation
            encoded_result = result_data.get("result")
            attestation = result_data.get("attestation", {})
            
            # Decode the result
            if encoded_result:
                serialized_result = base64.b64decode(encoded_result)
                result = pickle.loads(serialized_result)
            else:
                result = None
            
            return {
                "result": result,
                "attestation": attestation
            }
        except Exception as e:
            logger.error(f"Error in SGX execution: {e}")
            raise
    
    def get_enclave_info(self) -> Dict[str, Any]:
        """
        Get information about the SGX enclave.
        
        Returns:
            Dictionary with enclave information
        """
        try:
            response = requests.get(f"{self.enclave_url}/info")
            
            if response.status_code != 200:
                logger.error(f"Failed to get enclave info: {response.text}")
                raise Exception(f"Failed to get enclave info: {response.text}")
            
            return response.json()
        except Exception as e:
            logger.error(f"Error getting enclave info: {e}")
            raise
    
    def verify_attestation(self, attestation) -> bool:
        """
        Verify an attestation.
        
        Args:
            attestation: Attestation to verify
            
        Returns:
            Whether the attestation is valid
        """
        try:
            if not attestation or not isinstance(attestation, dict):
                return False
            
            # In a real implementation, this would verify the attestation
            # with the Intel Attestation Service (IAS)
            # For the dev container, we just check if the attestation has the required fields
            return (
                "hash" in attestation and
                "enclave_hash" in attestation and
                "timestamp" in attestation
            )
        except Exception as e:
            logger.error(f"Error verifying attestation: {e}")
            return False 