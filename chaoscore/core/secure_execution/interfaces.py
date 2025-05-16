"""
Secure Execution Interfaces

This module defines the interfaces for the Secure Execution Environment.
"""
import enum
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple


class ExecutionStatus(enum.Enum):
    """Status of code execution in the secure environment."""
    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"
    ERROR = "error"


class Attestation:
    """
    Represents an attestation of secure code execution.
    
    An attestation provides cryptographic proof that a specific piece of code
    was executed in a secure environment with specific inputs and outputs.
    """
    
    def get_id(self) -> str:
        """Get the unique identifier for this attestation."""
        pass
    
    def get_environment_info(self) -> Dict[str, Any]:
        """
        Get information about the secure environment where code was executed.
        
        This may include TEE type, version, measurements, etc.
        """
        pass
    
    def get_code_hash(self) -> str:
        """Get the cryptographic hash of the code that was executed."""
        pass
    
    def get_input_hash(self) -> str:
        """Get the cryptographic hash of the inputs to the code execution."""
        pass
    
    def get_output_hash(self) -> str:
        """Get the cryptographic hash of the outputs from the code execution."""
        pass
    
    def get_timestamp(self) -> int:
        """Get the timestamp when the attestation was created."""
        pass
    
    def get_signature(self) -> str:
        """Get the cryptographic signature of the attestation."""
        pass
    
    def get_public_key(self) -> str:
        """Get the public key that can verify the signature."""
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the attestation to a dictionary."""
        pass
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Attestation':
        """Create an attestation from a dictionary."""
        pass


class ExecutionResult:
    """
    Represents the result of code execution in a secure environment.
    
    This includes the outputs, status, and attestation.
    """
    
    def get_status(self) -> ExecutionStatus:
        """Get the status of the code execution."""
        pass
    
    def get_outputs(self) -> Dict[str, Any]:
        """Get the outputs from the code execution."""
        pass
    
    def get_logs(self) -> List[str]:
        """Get the logs from the code execution."""
        pass
    
    def get_attestation(self) -> Optional[Attestation]:
        """Get the attestation for the code execution."""
        pass
    
    def get_execution_time(self) -> float:
        """Get the execution time in seconds."""
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the execution result to a dictionary."""
        pass
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExecutionResult':
        """Create an execution result from a dictionary."""
        pass


class AttestationProvider(ABC):
    """
    Interface for attestation providers.
    
    An attestation provider is responsible for generating and verifying
    attestations for code execution.
    """
    
    @abstractmethod
    def generate_attestation(
        self,
        code_hash: str,
        input_hash: str,
        output_hash: str,
        environment_info: Dict[str, Any]
    ) -> Attestation:
        """
        Generate an attestation for code execution.
        
        Args:
            code_hash: Hash of the code that was executed
            input_hash: Hash of the inputs to the code execution
            output_hash: Hash of the outputs from the code execution
            environment_info: Information about the secure environment
            
        Returns:
            Attestation: The generated attestation
        """
        pass
    
    @abstractmethod
    def verify_attestation(self, attestation: Attestation) -> bool:
        """
        Verify an attestation.
        
        Args:
            attestation: The attestation to verify
            
        Returns:
            bool: True if the attestation is valid, False otherwise
        """
        pass


class SecureExecutionEnvironment(ABC):
    """
    Interface for secure execution environments.
    
    A secure execution environment provides an isolated environment for
    executing agent code with attestation.
    """
    
    @abstractmethod
    def execute(
        self,
        code: str,
        inputs: Dict[str, Any],
        timeout: Optional[float] = None,
        with_attestation: bool = True
    ) -> ExecutionResult:
        """
        Execute code in the secure environment.
        
        Args:
            code: The code to execute
            inputs: The inputs to the code execution
            timeout: Optional timeout in seconds
            with_attestation: Whether to generate an attestation
            
        Returns:
            ExecutionResult: The result of the code execution
        """
        pass
    
    @abstractmethod
    def execute_function(
        self,
        function_name: str,
        function_args: List[Any],
        function_kwargs: Dict[str, Any],
        module_path: str,
        timeout: Optional[float] = None,
        with_attestation: bool = True
    ) -> ExecutionResult:
        """
        Execute a function in the secure environment.
        
        Args:
            function_name: The name of the function to execute
            function_args: The positional arguments to the function
            function_kwargs: The keyword arguments to the function
            module_path: The path to the module containing the function
            timeout: Optional timeout in seconds
            with_attestation: Whether to generate an attestation
            
        Returns:
            ExecutionResult: The result of the function execution
        """
        pass
    
    @abstractmethod
    def get_environment_info(self) -> Dict[str, Any]:
        """
        Get information about the secure environment.
        
        Returns:
            Dict[str, Any]: Information about the secure environment
        """
        pass
    
    @abstractmethod
    def verify_environment(self) -> Tuple[bool, Optional[str]]:
        """
        Verify the integrity of the secure environment.
        
        Returns:
            Tuple[bool, Optional[str]]: A tuple containing a boolean indicating
                whether the environment is valid, and an optional error message
        """
        pass


# Exception classes
class SecureExecutionError(Exception):
    """Base exception for secure execution errors."""
    pass


class AttestationVerificationError(SecureExecutionError):
    """Exception raised when attestation verification fails."""
    pass


class EnvironmentSetupError(SecureExecutionError):
    """Exception raised when the secure environment cannot be set up."""
    pass


class ExecutionTimeoutError(SecureExecutionError):
    """Exception raised when code execution times out."""
    pass 