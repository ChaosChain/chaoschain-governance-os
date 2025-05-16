"""
PostgreSQL adapter for ChaosCore.

This module provides a PostgreSQL implementation of the DatabaseAdapter interface.
"""
import os
import json
from typing import Any, Dict, List, Optional, Tuple, Union
import psycopg2
from psycopg2.extras import RealDictCursor

from chaoscore.core.db.adapter import DatabaseAdapter


class PostgreSQLAdapter(DatabaseAdapter):
    """PostgreSQL adapter for ChaosCore."""

    def __init__(self, connection_string: Optional[str] = None):
        """
        Initialize the PostgreSQL adapter.

        Args:
            connection_string: Connection string for the PostgreSQL database.
                If None, it will try to use the DATABASE_URL environment variable.
        """
        self.connection_string = connection_string or os.environ.get("DATABASE_URL")
        if not self.connection_string:
            raise ValueError("PostgreSQL connection string not provided and DATABASE_URL not set")
        
        self.conn = None
        self.cursor = None
        self.connect()

    def connect(self) -> None:
        """Connect to the PostgreSQL database."""
        if self.conn is None:
            self.conn = psycopg2.connect(self.connection_string)
            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)

    def close(self) -> None:
        """Close the database connection."""
        if self.cursor:
            self.cursor.close()
            self.cursor = None
        
        if self.conn:
            self.conn.close()
            self.conn = None

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
        
        # RealDictCursor already returns dictionaries
        return dict(row)

    def fetchall(self) -> List[Dict[str, Any]]:
        """
        Fetch all rows from the result set.

        Returns:
            List of row data as dictionaries
        """
        if self.cursor is None:
            return []
        
        rows = self.cursor.fetchall()
        
        # RealDictCursor already returns dictionaries
        return [dict(row) for row in rows]

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
            metadata JSONB
        )
        """)
        
        # Create action logging table
        self.execute("""
        CREATE TABLE IF NOT EXISTS actions (
            id TEXT PRIMARY KEY,
            agent_id TEXT NOT NULL,
            action_type TEXT NOT NULL,
            description TEXT,
            data JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (agent_id) REFERENCES agents(id)
        )
        """)
        
        # Create action outcomes table
        self.execute("""
        CREATE TABLE IF NOT EXISTS action_outcomes (
            action_id TEXT PRIMARY KEY,
            success BOOLEAN NOT NULL,
            results JSONB,
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
            settings JSONB,
            FOREIGN KEY (owner_id) REFERENCES agents(id)
        )
        """)
        
        # Create studio members table
        self.execute("""
        CREATE TABLE IF NOT EXISTS studio_members (
            studio_id TEXT,
            agent_id TEXT,
            role TEXT NOT NULL,
            permissions JSONB,
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
            id SERIAL PRIMARY KEY,
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
        
        # Create indexes for performance
        self.execute("CREATE INDEX IF NOT EXISTS idx_actions_agent_id ON actions(agent_id)")
        self.execute("CREATE INDEX IF NOT EXISTS idx_reputation_agent_id ON reputation(agent_id)")
        self.execute("CREATE INDEX IF NOT EXISTS idx_reputation_history_agent_id ON reputation_history(agent_id)")
        
        self.commit() 