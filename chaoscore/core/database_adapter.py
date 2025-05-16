"""
Database adapter module for ChaosCore.

This module provides a unified interface for database adapters
and reexports concrete implementations.
"""
import os
import json
from typing import Optional, Dict, Any, List

from chaoscore.core.db.adapter import DatabaseAdapter
from chaoscore.core.db.sqlite_adapter import SQLiteAdapter
from chaoscore.core.db.postgres_adapter import PostgreSQLAdapter


def get_database_adapter() -> DatabaseAdapter:
    """
    Factory function to get the appropriate database adapter.
    
    Returns:
        A DatabaseAdapter instance
    """
    # Check if we should use SQLite for testing
    if os.environ.get("SQLITE_TEST_MODE", "false").lower() == "true":
        return SQLiteAdapter()
    
    # Check if we have a DATABASE_URL
    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        return PostgreSQLAdapter(database_url)
    
    # Default to SQLite in-memory
    return SQLiteAdapter()


# Re-export classes
__all__ = [
    "DatabaseAdapter",
    "SQLiteAdapter",
    "PostgreSQLAdapter",
    "get_database_adapter",
    "PostgreSQLAgentRegistry",
    "PostgreSQLProofOfAgency",
    "PostgreSQLReputationSystem"
]


class PostgreSQLAgentRegistry:
    """PostgreSQL implementation of the Agent Registry."""
    
    def __init__(self, db: DatabaseAdapter):
        """
        Initialize the agent registry.
        
        Args:
            db: Database adapter
        """
        self.db = db
    
    def create_agent(self, agent_id: str, name: str, email: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a new agent.
        
        Args:
            agent_id: Agent ID
            name: Agent name
            email: Agent email
            metadata: Agent metadata
            
        Returns:
            Agent ID
        """
        metadata_json = json.dumps(metadata or {})
        query = """
        INSERT INTO agents (id, name, email, metadata)
        VALUES (%s, %s, %s, %s)
        RETURNING id
        """
        self.db.execute(query, (agent_id, name, email, metadata_json))
        result = self.db.fetchone()
        self.db.commit()
        return result["id"]
    
    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Get an agent by ID.
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Agent data or None if not found
        """
        query = """
        SELECT id, name, email, created_at, updated_at, metadata
        FROM agents
        WHERE id = %s
        """
        self.db.execute(query, (agent_id,))
        agent = self.db.fetchone()
        
        if agent and isinstance(agent.get("metadata"), str):
            try:
                agent["metadata"] = json.loads(agent["metadata"])
            except (json.JSONDecodeError, TypeError):
                agent["metadata"] = {}
        
        return agent
    
    def list_agents(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        List agents.
        
        Args:
            limit: Maximum number of agents to return
            offset: Offset for pagination
            
        Returns:
            List of agents
        """
        query = """
        SELECT id, name, email, created_at, updated_at, metadata
        FROM agents
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
        """
        self.db.execute(query, (limit, offset))
        agents = self.db.fetchall()
        
        # Parse metadata JSON
        for agent in agents:
            if isinstance(agent.get("metadata"), str):
                try:
                    agent["metadata"] = json.loads(agent["metadata"])
                except (json.JSONDecodeError, TypeError):
                    agent["metadata"] = {}
        
        return agents
    
    def update_agent(self, agent_id: str, name: Optional[str] = None, email: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Update an agent.
        
        Args:
            agent_id: Agent ID
            name: New agent name
            email: New agent email
            metadata: New agent metadata
            
        Returns:
            True if successful, False otherwise
        """
        # Get current agent data
        current_agent = self.get_agent(agent_id)
        if not current_agent:
            return False
        
        # Update only provided fields
        updated_name = name if name is not None else current_agent["name"]
        updated_email = email if email is not None else current_agent["email"]
        
        # Handle metadata update
        if metadata is not None:
            updated_metadata = json.dumps(metadata)
        elif isinstance(current_agent.get("metadata"), dict):
            updated_metadata = json.dumps(current_agent["metadata"])
        else:
            updated_metadata = "{}"
        
        # Execute update
        query = """
        UPDATE agents
        SET name = %s, email = %s, metadata = %s, updated_at = CURRENT_TIMESTAMP
        WHERE id = %s
        """
        self.db.execute(query, (updated_name, updated_email, updated_metadata, agent_id))
        self.db.commit()
        
        return True
    
    def delete_agent(self, agent_id: str) -> bool:
        """
        Delete an agent.
        
        Args:
            agent_id: Agent ID
            
        Returns:
            True if successful, False otherwise
        """
        query = "DELETE FROM agents WHERE id = %s"
        self.db.execute(query, (agent_id,))
        rows_affected = self.db.cursor.rowcount if self.db.cursor else 0
        self.db.commit()
        
        return rows_affected > 0


class PostgreSQLProofOfAgency:
    """PostgreSQL implementation of Proof of Agency."""
    
    def __init__(self, db: DatabaseAdapter):
        """
        Initialize the proof of agency.
        
        Args:
            db: Database adapter
        """
        self.db = db
        self.anchor_client = None
    
    def set_anchor_client(self, client: Any) -> None:
        """
        Set the anchor client for blockchain integration.
        
        Args:
            client: Anchor client
        """
        self.anchor_client = client
    
    def log_action(self, action_id: str, agent_id: str, action_type: str, description: Optional[str] = None, data: Optional[Dict[str, Any]] = None) -> str:
        """
        Log an action.
        
        Args:
            action_id: Action ID
            agent_id: Agent ID
            action_type: Action type
            description: Action description
            data: Action data
            
        Returns:
            Action ID
        """
        data_json = json.dumps(data or {})
        query = """
        INSERT INTO actions (id, agent_id, action_type, description, data)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
        """
        self.db.execute(query, (action_id, agent_id, action_type, description, data_json))
        result = self.db.fetchone()
        self.db.commit()
        
        # Anchor to blockchain if available
        if self.anchor_client:
            try:
                self.anchor_client.anchor_action(action_id, agent_id, action_type)
            except Exception as e:
                print(f"Failed to anchor action: {e}")
        
        return result["id"]
    
    def record_outcome(self, action_id: str, success: bool, results: Optional[Dict[str, Any]] = None, impact_score: float = 0.0) -> bool:
        """
        Record an action outcome.
        
        Args:
            action_id: Action ID
            success: Whether the action was successful
            results: Action results
            impact_score: Impact score
            
        Returns:
            True if successful, False otherwise
        """
        results_json = json.dumps(results or {})
        query = """
        INSERT INTO action_outcomes (action_id, success, results, impact_score)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (action_id) DO UPDATE
        SET success = EXCLUDED.success, results = EXCLUDED.results, impact_score = EXCLUDED.impact_score
        """
        self.db.execute(query, (action_id, success, results_json, impact_score))
        self.db.commit()
        
        return True
    
    def get_action(self, action_id: str) -> Optional[Dict[str, Any]]:
        """
        Get an action by ID.
        
        Args:
            action_id: Action ID
            
        Returns:
            Action data or None if not found
        """
        query = """
        SELECT a.id, a.agent_id, a.action_type, a.description, a.data, a.created_at,
               o.success, o.results, o.impact_score, o.created_at as outcome_created_at
        FROM actions a
        LEFT JOIN action_outcomes o ON a.id = o.action_id
        WHERE a.id = %s
        """
        self.db.execute(query, (action_id,))
        action = self.db.fetchone()
        
        if not action:
            return None
        
        # Parse JSON fields
        if isinstance(action.get("data"), str):
            try:
                action["data"] = json.loads(action["data"])
            except (json.JSONDecodeError, TypeError):
                action["data"] = {}
        
        if isinstance(action.get("results"), str):
            try:
                action["results"] = json.loads(action["results"])
            except (json.JSONDecodeError, TypeError):
                action["results"] = {}
        
        return action
    
    def list_actions(self, agent_id: Optional[str] = None, action_type: Optional[str] = None, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        List actions.
        
        Args:
            agent_id: Filter by agent ID
            action_type: Filter by action type
            limit: Maximum number of actions to return
            offset: Offset for pagination
            
        Returns:
            List of actions
        """
        query_parts = [
            "SELECT a.id, a.agent_id, a.action_type, a.description, a.data, a.created_at,",
            "       o.success, o.results, o.impact_score, o.created_at as outcome_created_at",
            "FROM actions a",
            "LEFT JOIN action_outcomes o ON a.id = o.action_id",
            "WHERE 1=1"
        ]
        params = []
        
        if agent_id:
            query_parts.append("AND a.agent_id = %s")
            params.append(agent_id)
        
        if action_type:
            query_parts.append("AND a.action_type = %s")
            params.append(action_type)
        
        query_parts.append("ORDER BY a.created_at DESC")
        query_parts.append("LIMIT %s OFFSET %s")
        params.extend([limit, offset])
        
        query = " ".join(query_parts)
        self.db.execute(query, tuple(params))
        actions = self.db.fetchall()
        
        # Parse JSON fields
        for action in actions:
            if isinstance(action.get("data"), str):
                try:
                    action["data"] = json.loads(action["data"])
                except (json.JSONDecodeError, TypeError):
                    action["data"] = {}
            
            if isinstance(action.get("results"), str):
                try:
                    action["results"] = json.loads(action["results"])
                except (json.JSONDecodeError, TypeError):
                    action["results"] = {}
        
        return actions


class PostgreSQLReputationSystem:
    """PostgreSQL implementation of Reputation System."""
    
    def __init__(self, db: DatabaseAdapter):
        """
        Initialize the reputation system.
        
        Args:
            db: Database adapter
        """
        self.db = db
    
    def get_reputation(self, agent_id: str, category: Optional[str] = None) -> float:
        """
        Get an agent's reputation score.
        
        Args:
            agent_id: Agent ID
            category: Reputation category
            
        Returns:
            Reputation score
        """
        if category:
            query = """
            SELECT score
            FROM reputation
            WHERE agent_id = %s AND category = %s
            """
            self.db.execute(query, (agent_id, category))
        else:
            query = """
            SELECT AVG(score) as score
            FROM reputation
            WHERE agent_id = %s
            """
            self.db.execute(query, (agent_id,))
        
        result = self.db.fetchone()
        
        if not result or result.get("score") is None:
            return 0.5  # Default neutral score
        
        return float(result["score"])
    
    def update_reputation(self, agent_id: str, score_delta: float, category: Optional[str] = None, reason: Optional[str] = None, action_id: Optional[str] = None) -> bool:
        """
        Update an agent's reputation.
        
        Args:
            agent_id: Agent ID
            score_delta: Score delta
            category: Reputation category
            reason: Reason for update
            action_id: Related action ID
            
        Returns:
            True if successful, False otherwise
        """
        category = category or "general"
        
        # Record history
        history_query = """
        INSERT INTO reputation_history (agent_id, category, score_delta, reason, action_id)
        VALUES (%s, %s, %s, %s, %s)
        """
        self.db.execute(history_query, (agent_id, category, score_delta, reason, action_id))
        
        # Get current score or default
        current_score = self.get_reputation(agent_id, category)
        
        # Calculate new score (constrain between 0 and 1)
        new_score = max(0, min(1, current_score + score_delta))
        
        # Update or insert score
        upsert_query = """
        INSERT INTO reputation (agent_id, category, score, updated_at)
        VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
        ON CONFLICT (agent_id, category) DO UPDATE
        SET score = %s, updated_at = CURRENT_TIMESTAMP
        """
        self.db.execute(upsert_query, (agent_id, category, new_score, new_score))
        self.db.commit()
        
        return True
    
    def get_history(self, agent_id: str, category: Optional[str] = None, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get an agent's reputation history.
        
        Args:
            agent_id: Agent ID
            category: Reputation category
            limit: Maximum number of history entries to return
            offset: Offset for pagination
            
        Returns:
            List of history entries
        """
        query_parts = [
            "SELECT id, agent_id, category, score_delta, reason, action_id, created_at",
            "FROM reputation_history",
            "WHERE agent_id = %s"
        ]
        params = [agent_id]
        
        if category:
            query_parts.append("AND category = %s")
            params.append(category)
        
        query_parts.append("ORDER BY created_at DESC")
        query_parts.append("LIMIT %s OFFSET %s")
        params.extend([limit, offset])
        
        query = " ".join(query_parts)
        self.db.execute(query, tuple(params))
        return self.db.fetchall()
    
    def get_top_agents(self, category: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get top agents by reputation.
        
        Args:
            category: Reputation category
            limit: Maximum number of agents to return
            
        Returns:
            List of top agents
        """
        if category:
            query = """
            SELECT r.agent_id, r.score, r.updated_at, a.name
            FROM reputation r
            JOIN agents a ON r.agent_id = a.id
            WHERE r.category = %s
            ORDER BY r.score DESC
            LIMIT %s
            """
            self.db.execute(query, (category, limit))
        else:
            query = """
            SELECT r.agent_id, AVG(r.score) as score, MAX(r.updated_at) as updated_at, a.name
            FROM reputation r
            JOIN agents a ON r.agent_id = a.id
            GROUP BY r.agent_id, a.name
            ORDER BY AVG(r.score) DESC
            LIMIT %s
            """
            self.db.execute(query, (limit,))
        
        return self.db.fetchall() 