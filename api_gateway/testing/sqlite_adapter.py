"""
SQLite Adapter for Testing

This module provides a SQLite-based adapter for testing the API Gateway.
"""

import os
import sqlite3
import logging
import json
from typing import Dict, Any, Optional, List
from uuid import uuid4

# Set up logging
logger = logging.getLogger(__name__)

class SQLiteAdapter:
    """
    SQLite adapter for testing.
    
    This adapter implements the same interface as PostgreSQLAdapter,
    but uses SQLite for testing.
    """
    
    def __init__(self, db_path=":memory:"):
        """
        Initialize the SQLite adapter.
        
        Args:
            db_path: Path to the SQLite database file, or :memory: for in-memory
        """
        self.db_path = db_path
        self.conn = None
        self._initialize_db()
    
    def _initialize_db(self):
        """
        Initialize the database schema.
        """
        self.connect()
        
        # Create tables
        with self.conn:
            # Agent Registry tables
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS agents (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS agent_metadata (
                    agent_id TEXT,
                    key TEXT NOT NULL,
                    value TEXT NOT NULL,
                    PRIMARY KEY (agent_id, key),
                    FOREIGN KEY (agent_id) REFERENCES agents(id)
                )
            """)
            
            # Proof of Agency tables
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS actions (
                    id TEXT PRIMARY KEY,
                    agent_id TEXT,
                    action_type TEXT NOT NULL,
                    description TEXT NOT NULL,
                    timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    anchored INTEGER NOT NULL DEFAULT 0,
                    tx_hash TEXT,
                    FOREIGN KEY (agent_id) REFERENCES agents(id)
                )
            """)
            
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS action_data (
                    action_id TEXT,
                    key TEXT NOT NULL,
                    value TEXT NOT NULL,
                    PRIMARY KEY (action_id, key),
                    FOREIGN KEY (action_id) REFERENCES actions(id)
                )
            """)
            
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS outcomes (
                    action_id TEXT PRIMARY KEY,
                    success INTEGER NOT NULL,
                    impact_score REAL NOT NULL DEFAULT 0,
                    timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    anchored INTEGER NOT NULL DEFAULT 0,
                    tx_hash TEXT,
                    FOREIGN KEY (action_id) REFERENCES actions(id)
                )
            """)
            
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS outcome_results (
                    action_id TEXT,
                    key TEXT NOT NULL,
                    value TEXT NOT NULL,
                    PRIMARY KEY (action_id, key),
                    FOREIGN KEY (action_id) REFERENCES outcomes(action_id)
                )
            """)
            
            # Reputation System tables
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS reputation_scores (
                    agent_id TEXT,
                    context TEXT NOT NULL DEFAULT 'global',
                    score REAL NOT NULL DEFAULT 0,
                    last_updated TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (agent_id, context),
                    FOREIGN KEY (agent_id) REFERENCES agents(id)
                )
            """)
            
            # Metrics tables
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    value INTEGER NOT NULL,
                    timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Insert initial metrics
            self.conn.execute("INSERT OR IGNORE INTO metrics (name, value) VALUES ('agent_count', 0)")
            self.conn.execute("INSERT OR IGNORE INTO metrics (name, value) VALUES ('action_count', 0)")
            self.conn.execute("INSERT OR IGNORE INTO metrics (name, value) VALUES ('simulation_count', 0)")
            self.conn.execute("INSERT OR IGNORE INTO metrics (name, value) VALUES ('anchoring_count', 0)")
    
    def connect(self):
        """
        Connect to the SQLite database.
        
        Returns:
            Connection object
        """
        if self.conn is None:
            try:
                self.conn = sqlite3.connect(self.db_path)
                self.conn.row_factory = sqlite3.Row
                logger.info(f"Connected to SQLite database at {self.db_path}")
            except sqlite3.Error as e:
                logger.error(f"Error connecting to SQLite: {e}")
                raise
        return self.conn
    
    def execute(self, query, params=None, fetch=None):
        """
        Execute a SQL query.
        
        Args:
            query: SQL query
            params: Query parameters
            fetch: 'one', 'all', or None for no fetch
            
        Returns:
            Query result or None
        """
        conn = self.connect()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params or {})
            
            if fetch == 'one':
                result = cursor.fetchone()
                if result:
                    return dict(result)
                return None
            elif fetch == 'all':
                result = cursor.fetchall()
                return [dict(row) for row in result]
            else:
                conn.commit()
                return None
        except sqlite3.Error as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
    
    def close(self):
        """
        Close the database connection.
        """
        if self.conn:
            self.conn.close()
            self.conn = None
            logger.info("Closed SQLite connection")
    
    def __enter__(self):
        """
        Context manager entry.
        
        Returns:
            self
        """
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit.
        
        Args:
            exc_type: Exception type
            exc_val: Exception value
            exc_tb: Exception traceback
        """
        self.close()

    # Agent Registry methods
    def register_agent(self, name, email, metadata=None):
        """Register a new agent."""
        agent_id = f"agent-{uuid4()}"
        
        self.execute(
            "INSERT INTO agents (id, name, email) VALUES (?, ?, ?)",
            (agent_id, name, email)
        )
        
        if metadata:
            for key, value in metadata.items():
                self.execute(
                    "INSERT INTO agent_metadata (agent_id, key, value) VALUES (?, ?, ?)",
                    (agent_id, key, str(value))
                )
        
        self.execute(
            "UPDATE metrics SET value = value + 1 WHERE name = 'agent_count'"
        )
        
        return agent_id
    
    def get_agent(self, agent_id):
        """Get agent by ID."""
        agent = self.execute(
            "SELECT * FROM agents WHERE id = ?",
            (agent_id,),
            fetch='one'
        )
        
        if not agent:
            return None
        
        metadata_rows = self.execute(
            "SELECT key, value FROM agent_metadata WHERE agent_id = ?",
            (agent_id,),
            fetch='all'
        )
        
        metadata = {row['key']: row['value'] for row in (metadata_rows or [])}
        
        # Create an agent object with the same interface as PostgreSQLAgentRegistry
        class Agent:
            def __init__(self, agent_id, name, email, metadata):
                self.agent_id = agent_id
                self.name = name
                self.email = email
                self.metadata = metadata
            
            def get_id(self):
                return self.agent_id
            
            def get_name(self):
                return self.name
            
            def get_email(self):
                return self.email
            
            def get_metadata(self):
                return self.metadata
        
        return Agent(
            agent_id=agent['id'],
            name=agent['name'],
            email=agent['email'],
            metadata=metadata
        )
    
    def list_agents(self, limit=100, offset=0):
        """List agents with pagination."""
        agents = self.execute(
            "SELECT * FROM agents ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (limit, offset),
            fetch='all'
        )
        
        result = []
        for agent in agents:
            metadata_rows = self.execute(
                "SELECT key, value FROM agent_metadata WHERE agent_id = ?",
                (agent['id'],),
                fetch='all'
            )
            
            metadata = {row['key']: row['value'] for row in (metadata_rows or [])}
            
            class Agent:
                def __init__(self, agent_id, name, email, metadata):
                    self.agent_id = agent_id
                    self.name = name
                    self.email = email
                    self.metadata = metadata
                
                def get_id(self):
                    return self.agent_id
                
                def get_name(self):
                    return self.name
                
                def get_email(self):
                    return self.email
                
                def get_metadata(self):
                    return self.metadata
            
            result.append(Agent(
                agent_id=agent['id'],
                name=agent['name'],
                email=agent['email'],
                metadata=metadata
            ))
        
        return result
    
    # Proof of Agency methods
    def log_action(self, agent_id, action_type, description, data=None):
        """Log an agent action."""
        action_id = f"action-{uuid4()}"
        
        self.execute(
            """
            INSERT INTO actions (id, agent_id, action_type, description)
            VALUES (?, ?, ?, ?)
            """,
            (action_id, agent_id, action_type, description)
        )
        
        if data:
            for key, value in data.items():
                self.execute(
                    """
                    INSERT INTO action_data (action_id, key, value)
                    VALUES (?, ?, ?)
                    """,
                    (action_id, key, str(value))
                )
        
        self.execute(
            "UPDATE metrics SET value = value + 1 WHERE name = 'action_count'"
        )
        
        if action_type == 'SIMULATE':
            self.execute(
                "UPDATE metrics SET value = value + 1 WHERE name = 'simulation_count'"
            )
        
        return action_id
    
    def record_outcome(self, action_id, success, results=None, impact_score=0.0):
        """Record the outcome of an action."""
        try:
            self.execute(
                """
                INSERT INTO outcomes (action_id, success, impact_score)
                VALUES (?, ?, ?)
                """,
                (action_id, 1 if success else 0, impact_score)
            )
            
            if results:
                for key, value in results.items():
                    self.execute(
                        """
                        INSERT INTO outcome_results (action_id, key, value)
                        VALUES (?, ?, ?)
                        """,
                        (action_id, key, str(value))
                    )
            
            return True
        except Exception as e:
            logger.error(f"Error recording outcome: {e}")
            return False
    
    # Reputation System methods
    def update_reputation(self, agent_id, delta, context='global'):
        """Update agent reputation."""
        score = self.execute(
            """
            SELECT score FROM reputation_scores
            WHERE agent_id = ? AND context = ?
            """,
            (agent_id, context),
            fetch='one'
        )
        
        if score:
            new_score = score['score'] + delta
            self.execute(
                """
                UPDATE reputation_scores
                SET score = ?, last_updated = CURRENT_TIMESTAMP
                WHERE agent_id = ? AND context = ?
                """,
                (new_score, agent_id, context)
            )
        else:
            new_score = delta
            self.execute(
                """
                INSERT INTO reputation_scores (agent_id, context, score)
                VALUES (?, ?, ?)
                """,
                (agent_id, context, new_score)
            )
        
        return new_score
    
    def get_reputation(self, agent_id, context='global'):
        """Get agent reputation."""
        score = self.execute(
            """
            SELECT score FROM reputation_scores
            WHERE agent_id = ? AND context = ?
            """,
            (agent_id, context),
            fetch='one'
        )
        
        return score['score'] if score else 0.0
    
    def get_top_agents(self, context='global', limit=10):
        """Get top agents by reputation."""
        results = self.execute(
            """
            SELECT a.id, a.name, r.score
            FROM reputation_scores r
            JOIN agents a ON r.agent_id = a.id
            WHERE r.context = ?
            ORDER BY r.score DESC
            LIMIT ?
            """,
            (context, limit),
            fetch='all'
        )
        
        return results 