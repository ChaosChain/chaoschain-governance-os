"""
Task Result Model

This module provides an enhanced TaskResult model with support for markdown summaries
and blockchain receipts.
"""

import logging
import time
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class TaskResult:
    """
    Enhanced task result model that supports markdown summaries and blockchain receipts.
    
    This class extends the basic task result model to include additional fields
    for better human readability and blockchain integration.
    """
    
    def __init__(
        self,
        task_id: str,
        task_name: str,
        success: bool,
        output: Dict[str, Any],
        markdown_summary: Optional[str] = None,
        receipt_tx_hash: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        timestamp: Optional[int] = None
    ):
        """
        Initialize the task result.
        
        Args:
            task_id: Unique identifier for the task
            task_name: Name of the task
            success: Whether the task completed successfully
            output: Task output data
            markdown_summary: Optional markdown summary of the results
            receipt_tx_hash: Optional transaction hash for the receipt on the blockchain
            metadata: Optional metadata about the execution
            timestamp: Execution timestamp (defaults to current time)
        """
        self.task_id = task_id
        self.task_name = task_name
        self.success = success
        self.output = output
        self.markdown_summary = markdown_summary
        self.receipt_tx_hash = receipt_tx_hash
        self.metadata = metadata or {}
        self.timestamp = timestamp or int(time.time())
    
    def get_task_id(self) -> str:
        """Get the task ID."""
        return self.task_id
    
    def get_task_name(self) -> str:
        """Get the task name."""
        return self.task_name
    
    def get_success(self) -> bool:
        """Get the success status."""
        return self.success
    
    def get_output(self) -> Dict[str, Any]:
        """Get the output data."""
        return self.output
    
    def get_markdown_summary(self) -> Optional[str]:
        """Get the markdown summary."""
        return self.markdown_summary
    
    def get_receipt_tx_hash(self) -> Optional[str]:
        """Get the blockchain receipt transaction hash."""
        return self.receipt_tx_hash
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get the metadata."""
        return self.metadata
    
    def get_timestamp(self) -> int:
        """Get the timestamp."""
        return self.timestamp
    
    def get_timestamp_iso(self) -> str:
        """Get the timestamp as an ISO format string."""
        dt = datetime.fromtimestamp(self.timestamp)
        return dt.isoformat()
    
    def set_markdown_summary(self, markdown_summary: str) -> None:
        """Set the markdown summary."""
        self.markdown_summary = markdown_summary
    
    def set_receipt_tx_hash(self, tx_hash: str) -> None:
        """Set the blockchain receipt transaction hash."""
        self.receipt_tx_hash = tx_hash
    
    def add_metadata(self, key: str, value: Any) -> None:
        """Add a metadata entry."""
        self.metadata[key] = value
    
    def get_etherscan_url(self, network: str = "goerli") -> Optional[str]:
        """
        Get the Etherscan URL for the receipt transaction.
        
        Args:
            network: Ethereum network name
            
        Returns:
            Etherscan URL or None if no receipt exists
        """
        if not self.receipt_tx_hash:
            return None
        
        base_urls = {
            "mainnet": "https://etherscan.io",
            "goerli": "https://goerli.etherscan.io",
            "sepolia": "https://sepolia.etherscan.io"
        }
        
        base_url = base_urls.get(network.lower(), base_urls["goerli"])
        return f"{base_url}/tx/{self.receipt_tx_hash}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the task result to a dictionary."""
        return {
            "task_id": self.task_id,
            "task_name": self.task_name,
            "success": self.success,
            "output": self.output,
            "markdown_summary": self.markdown_summary,
            "receipt_tx_hash": self.receipt_tx_hash,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
            "timestamp_iso": self.get_timestamp_iso()
        }
    
    def to_json(self, pretty: bool = False) -> str:
        """
        Convert the task result to a JSON string.
        
        Args:
            pretty: Whether to pretty-print the JSON
            
        Returns:
            JSON string representation
        """
        if pretty:
            return json.dumps(self.to_dict(), indent=2, sort_keys=True)
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaskResult':
        """
        Create a task result from a dictionary.
        
        Args:
            data: Dictionary representation
            
        Returns:
            TaskResult instance
        """
        return cls(
            task_id=data.get("task_id", ""),
            task_name=data.get("task_name", ""),
            success=data.get("success", False),
            output=data.get("output", {}),
            markdown_summary=data.get("markdown_summary"),
            receipt_tx_hash=data.get("receipt_tx_hash"),
            metadata=data.get("metadata", {}),
            timestamp=data.get("timestamp", int(time.time()))
        )
    
    @classmethod
    def from_task_output(
        cls,
        task_id: str,
        task_name: str,
        output: Dict[str, Any],
        markdown_summary: Optional[str] = None
    ) -> 'TaskResult':
        """
        Create a task result from a task output dictionary.
        
        Args:
            task_id: Task ID
            task_name: Task name
            output: Task output dictionary
            markdown_summary: Optional markdown summary
            
        Returns:
            TaskResult instance
        """
        success = output.get("success", False)
        metadata = {
            "risk_level": output.get("risk_level", "unknown"),
            "risk_score": output.get("risk_score", 0.0)
        }
        
        if "metadata" in output:
            metadata.update(output["metadata"])
            
        return cls(
            task_id=task_id,
            task_name=task_name,
            success=success,
            output=output,
            markdown_summary=markdown_summary or output.get("markdown_summary"),
            metadata=metadata,
            timestamp=output.get("timestamp", int(time.time()))
        ) 