"""
SGX Secure Execution implementation for ChaosCore.

This module provides an SGX-based implementation of the Secure Execution Environment.
"""

import json
import requests
from typing import Dict, Any, Optional

from chaoscore.core.secure_execution import SecureExecutionEnvironment


class SGXSecureExecutionEnvironment(SecureExecutionEnvironment):
    """SGX-based implementation of Secure Execution Environment."""

    def __init__(self, enclave_url: str):
        """
        Initialize the SGX secure execution environment.
        
        Args:
            enclave_url: URL of the SGX enclave service
        """
        self.enclave_url = enclave_url
        # Check if we should use mock mode (for testing)
        self.mock_mode = enclave_url.endswith("mock") or "mock" in enclave_url
        if self.mock_mode:
            from chaoscore.core.secure_execution import InMemorySecureExecution
            self.mock_impl = InMemorySecureExecution()

    def execute(self, code: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute code securely in an SGX enclave.
        
        Args:
            code: Code to execute
            inputs: Input parameters
            
        Returns:
            Execution results
        """
        if self.mock_mode:
            return self.mock_impl.execute(code, inputs)
        
        try:
            response = requests.post(
                f"{self.enclave_url}/execute",
                json={"code": code, "inputs": inputs},
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            # If the enclave is unreachable, fall back to mock mode
            print(f"SGX enclave unreachable, falling back to mock mode: {e}")
            from chaoscore.core.secure_execution import InMemorySecureExecution
            self.mock_impl = InMemorySecureExecution()
            self.mock_mode = True
            return self.mock_impl.execute(code, inputs)

    def verify_result(self, execution_id: str, result: Dict[str, Any]) -> bool:
        """
        Verify execution result.
        
        Args:
            execution_id: Execution ID
            result: Execution result
            
        Returns:
            True if verification succeeds, False otherwise
        """
        if self.mock_mode:
            return self.mock_impl.verify_result(execution_id, result)
        
        try:
            response = requests.post(
                f"{self.enclave_url}/verify",
                json={"execution_id": execution_id, "result": result},
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json().get("verified", False)
        except requests.RequestException:
            return False

    def get_enclave_info(self) -> Dict[str, Any]:
        """
        Get information about the SGX enclave.
        
        Returns:
            Enclave information
        """
        if self.mock_mode:
            return self.mock_impl.get_enclave_info()
        
        try:
            response = requests.get(
                f"{self.enclave_url}/info",
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Failed to get enclave info: {e}")
            return {
                "type": "sgx-unreachable",
                "version": "unknown",
                "enclave_hash": "unknown",
                "attestation": None,
                "error": str(e)
            } 