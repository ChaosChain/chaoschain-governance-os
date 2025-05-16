"""
SQLite adapter for ChaosCore.

This module provides a SQLite implementation of the DatabaseAdapter interface.
"""
import os
import sqlite3
from typing import Any, Dict, List, Optional, Tuple, Union

from chaoscore.core.db.adapter import DatabaseAdapter


class SQLiteAdapter(DatabaseAdapter):
    """SQLite adapter for ChaosCore."""

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the SQLite adapter.

        Args:
            db_path: Path to the SQLite database file. If None, an in-memory database is used.
        """
        self.db_path = db_path or ":memory:"
        self.conn = None
        self.cursor = None
        self.connect()

    def connect(self) -> None:
        """Connect to the SQLite database."""
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path)
            # Configure SQLite to return rows as dictionaries
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()

    def close(self) -> None:
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None

    def execute(self, query: str, params: Optional[Union[Dict[str, Any], List[Any], Tuple[Any, ...]]] = None) -> Any:
        """
        Execute a query.

        Args:
            query: SQL query to execute
            params: Query parameters

        Returns:
            Query result
        """
        if self.cursor is None:
            self.connect()
        
        if params is None:
            return self.cursor.execute(query)
        else:
            return self.cursor.execute(query, params)

    def fetchone(self) -> Optional[Dict[str, Any]]:
        """
        Fetch one row from the result set.

        Returns:
            Row data as a dictionary or None if no more rows
        """
        if self.cursor is None:
            return None
        
        row = self.cursor.fetchone()
        if row is None:
            return None
        
        # Convert sqlite3.Row to dictionary
        return {key: row[key] for key in row.keys()}

    def fetchall(self) -> List[Dict[str, Any]]:
        """
        Fetch all rows from the result set.

        Returns:
            List of row data as dictionaries
        """
        if self.cursor is None:
            return []
        
        rows = self.cursor.fetchall()
        
        # Convert sqlite3.Row objects to dictionaries
        return [{key: row[key] for key in row.keys()} for row in rows]

    def commit(self) -> None:
        """Commit the current transaction."""
        if self.conn:
            self.conn.commit()

    def rollback(self) -> None:
        """Roll back the current transaction."""
        if self.conn:
            self.conn.rollback()

    def create_tables(self) -> None:
        """Create required tables if they don't exist."""
        # Create agent registry table
        self.execute("""
        CREATE TABLE IF NOT EXISTS agents (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            metadata TEXT
        )
        """)
        
        # Create action logging table
        self.execute("""
        CREATE TABLE IF NOT EXISTS actions (
            id TEXT PRIMARY KEY,
            agent_id TEXT NOT NULL,
            action_type TEXT NOT NULL,
            description TEXT,
            data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (agent_id) REFERENCES agents(id)
        )
        """)
        
        # Create action outcomes table
        self.execute("""
        CREATE TABLE IF NOT EXISTS action_outcomes (
            action_id TEXT PRIMARY KEY,
            success BOOLEAN NOT NULL,
            results TEXT,
            impact_score REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (action_id) REFERENCES actions(id)
        )
        """)
        
        # Create studios table
        self.execute("""
        CREATE TABLE IF NOT EXISTS studios (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            owner_id TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            settings TEXT,
            FOREIGN KEY (owner_id) REFERENCES agents(id)
        )
        """)
        
        # Create studio members table
        self.execute("""
        CREATE TABLE IF NOT EXISTS studio_members (
            studio_id TEXT,
            agent_id TEXT,
            role TEXT NOT NULL,
            permissions TEXT,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (studio_id, agent_id),
            FOREIGN KEY (studio_id) REFERENCES studios(id),
            FOREIGN KEY (agent_id) REFERENCES agents(id)
        )
        """)
        
        # Create reputation table
        self.execute("""
        CREATE TABLE IF NOT EXISTS reputation (
            agent_id TEXT,
            category TEXT,
            score REAL NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (agent_id, category),
            FOREIGN KEY (agent_id) REFERENCES agents(id)
        )
        """)
        
        # Create reputation history table
        self.execute("""
        CREATE TABLE IF NOT EXISTS reputation_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id TEXT NOT NULL,
            category TEXT,
            score_delta REAL NOT NULL,
            reason TEXT,
            action_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (agent_id) REFERENCES agents(id),
            FOREIGN KEY (action_id) REFERENCES actions(id)
        )
        """)
        
        self.commit() 