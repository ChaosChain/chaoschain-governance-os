"""
Database adapter interface for ChaosCore.

This module defines the interface for database adapters used by ChaosCore.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, Union


class DatabaseAdapter(ABC):
    """Database adapter interface."""

    @abstractmethod
    def connect(self) -> None:
        """Connect to the database."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the database connection."""
        pass

    @abstractmethod
    def execute(self, query: str, params: Optional[Union[Dict[str, Any], List[Any], Tuple[Any, ...]]] = None) -> Any:
        """
        Execute a query.

        Args:
            query: SQL query to execute
            params: Query parameters

        Returns:
            Query result
        """
        pass

    @abstractmethod
    def fetchone(self) -> Optional[Dict[str, Any]]:
        """
        Fetch one row from the result set.

        Returns:
            Row data as a dictionary or None if no more rows
        """
        pass

    @abstractmethod
    def fetchall(self) -> List[Dict[str, Any]]:
        """
        Fetch all rows from the result set.

        Returns:
            List of row data as dictionaries
        """
        pass

    @abstractmethod
    def commit(self) -> None:
        """Commit the current transaction."""
        pass

    @abstractmethod
    def rollback(self) -> None:
        """Roll back the current transaction."""
        pass

    @abstractmethod
    def create_tables(self) -> None:
        """Create required tables if they don't exist."""
        pass 