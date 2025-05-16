"""
Database Adapter for ChaosCore

This module provides a PostgreSQL adapter for the ChaosCore components.
"""
import os
import logging
from typing import Dict, Any, Optional, List
import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)


class PostgreSQLAdapter:
    """
    PostgreSQL adapter for ChaosCore components.
    """
    
    def __init__(self, connection_params=None):
        """
        Initialize the PostgreSQL adapter.
        
        Args:
            connection_params: Optional connection parameters
        """
        self.connection_params = connection_params or {
            'user': os.environ.get('POSTGRES_USER', 'chaoscore'),
            'password': os.environ.get('POSTGRES_PASSWORD', 'chaoscore_pass'),
            'host': os.environ.get('POSTGRES_HOST', 'localhost'),
            'port': os.environ.get('POSTGRES_PORT', '5432'),
            'database': os.environ.get('POSTGRES_DB', 'chaoscore')
        }
        self.conn = None
    
    def connect(self):
        """
        Connect to the PostgreSQL database.
        
        Returns:
            Connection object
        """
        if self.conn is None or self.conn.closed:
            try:
                self.conn = psycopg2.connect(**self.connection_params)
                logger.info("Connected to PostgreSQL database")
            except psycopg2.Error as e:
                logger.error(f"Error connecting to PostgreSQL: {e}")
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
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params or {})
                
                if fetch == 'one':
                    result = cur.fetchone()
                elif fetch == 'all':
                    result = cur.fetchall()
                else:
                    result = None
                
                conn.commit()
                return result
        except psycopg2.Error as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
    
    def close(self):
        """
        Close the database connection.
        """
        if self.conn and not self.conn.closed:
            self.conn.close()
            logger.info("Closed PostgreSQL connection")
    
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


class PostgreSQLAgentRegistry:
    """
    PostgreSQL implementation of the Agent Registry.
    """
    
    def __init__(self, db=None):
        """
        Initialize the PostgreSQL Agent Registry.
        
        Args:
            db: Optional database adapter
        """
        self.db = db or PostgreSQLAdapter()
    
    def register_agent(self, name, email, metadata=None):
        """
        Register a new agent.
        
        Args:
            name: Agent name
            email: Agent email
            metadata: Optional agent metadata
            
        Returns:
            Agent ID
        """
        from uuid import uuid4
        
        # Generate ID
        agent_id = f"agent-{uuid4()}"
        
        # Insert agent
        self.db.execute(
            "INSERT INTO agents (id, name, email) VALUES (%(id)s, %(name)s, %(email)s)",
            {'id': agent_id, 'name': name, 'email': email}
        )
        
        # Insert metadata
        if metadata:
            for key, value in metadata.items():
                self.db.execute(
                    "INSERT INTO agent_metadata (agent_id, key, value) VALUES (%(agent_id)s, %(key)s, %(value)s)",
                    {'agent_id': agent_id, 'key': key, 'value': str(value)}
                )
        
        # Update metrics
        self.db.execute(
            "UPDATE metrics SET value = value + 1 WHERE name = 'agent_count'"
        )
        
        return agent_id
    
    def get_agent(self, agent_id):
        """
        Get agent information.
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Agent object or None
        """
        # Get agent
        agent = self.db.execute(
            "SELECT * FROM agents WHERE id = %(id)s",
            {'id': agent_id},
            fetch='one'
        )
        
        if not agent:
            return None
        
        # Get metadata
        metadata_rows = self.db.execute(
            "SELECT key, value FROM agent_metadata WHERE agent_id = %(agent_id)s",
            {'agent_id': agent_id},
            fetch='all'
        )
        
        metadata = {row['key']: row['value'] for row in (metadata_rows or [])}
        
        # Create agent object
        from chaoscore.core.agent_registry import Agent
        return Agent(
            agent_id=agent['id'],
            name=agent['name'],
            email=agent['email'],
            metadata=metadata
        )
    
    def list_agents(self, limit=100, offset=0):
        """
        List agents.
        
        Args:
            limit: Maximum number of agents to return
            offset: Offset for pagination
            
        Returns:
            List of agents
        """
        # Get agents
        agents = self.db.execute(
            "SELECT * FROM agents ORDER BY created_at DESC LIMIT %(limit)s OFFSET %(offset)s",
            {'limit': limit, 'offset': offset},
            fetch='all'
        )
        
        result = []
        for agent in agents:
            # Get metadata
            metadata_rows = self.db.execute(
                "SELECT key, value FROM agent_metadata WHERE agent_id = %(agent_id)s",
                {'agent_id': agent['id']},
                fetch='all'
            )
            
            metadata = {row['key']: row['value'] for row in (metadata_rows or [])}
            
            # Create agent object
            from chaoscore.core.agent_registry import Agent
            result.append(Agent(
                agent_id=agent['id'],
                name=agent['name'],
                email=agent['email'],
                metadata=metadata
            ))
        
        return result


class PostgreSQLProofOfAgency:
    """
    PostgreSQL implementation of the Proof of Agency.
    """
    
    def __init__(self, db=None):
        """
        Initialize the PostgreSQL Proof of Agency.
        
        Args:
            db: Optional database adapter
        """
        self.db = db or PostgreSQLAdapter()
        self.anchor_client = None
    
    def set_anchor_client(self, client):
        """
        Set the anchor client for blockchain anchoring.
        
        Args:
            client: Anchor client
        """
        self.anchor_client = client
    
    def log_action(self, agent_id, action_type, description, data=None):
        """
        Log an action.
        
        Args:
            agent_id: Agent ID
            action_type: Type of action
            description: Action description
            data: Optional action data
            
        Returns:
            Action ID
        """
        from uuid import uuid4
        
        # Generate ID
        action_id = f"action-{uuid4()}"
        
        # Insert action
        self.db.execute(
            """
            INSERT INTO actions (id, agent_id, action_type, description)
            VALUES (%(id)s, %(agent_id)s, %(action_type)s, %(description)s)
            """,
            {'id': action_id, 'agent_id': agent_id, 'action_type': action_type, 'description': description}
        )
        
        # Insert data
        if data:
            for key, value in data.items():
                self.db.execute(
                    """
                    INSERT INTO action_data (action_id, key, value)
                    VALUES (%(action_id)s, %(key)s, %(value)s)
                    """,
                    {'action_id': action_id, 'key': key, 'value': str(value)}
                )
        
        # Update metrics
        self.db.execute(
            "UPDATE metrics SET value = value + 1 WHERE name = 'action_count'"
        )
        
        # If action type is SIMULATE, update simulation count
        if action_type == 'SIMULATE':
            self.db.execute(
                "UPDATE metrics SET value = value + 1 WHERE name = 'simulation_count'"
            )
        
        # Anchor the action if an anchor client is set
        if self.anchor_client:
            try:
                result = self.anchor_client.anchor_action(
                    action_id=action_id,
                    agent_id=agent_id,
                    action_type=action_type,
                    metadata_uri=f"ipfs://{action_id}"  # In a real implementation, we would store actual metadata
                )
                
                # Update action with anchoring information
                self.db.execute(
                    "UPDATE actions SET anchored = TRUE, tx_hash = %(tx_hash)s WHERE id = %(id)s",
                    {'id': action_id, 'tx_hash': result.get('tx_hash')}
                )
                
                # Update metrics
                self.db.execute(
                    "UPDATE metrics SET value = value + 1 WHERE name = 'anchoring_count'"
                )
            except Exception as e:
                logger.error(f"Error anchoring action: {e}")
        
        return action_id
    
    def record_outcome(self, action_id, success, results=None, impact_score=0.0):
        """
        Record the outcome of an action.
        
        Args:
            action_id: Action ID
            success: Whether the action was successful
            results: Optional action results
            impact_score: Impact score of the action
            
        Returns:
            Whether the outcome was recorded successfully
        """
        try:
            # Insert outcome
            self.db.execute(
                """
                INSERT INTO outcomes (action_id, success, impact_score)
                VALUES (%(action_id)s, %(success)s, %(impact_score)s)
                """,
                {'action_id': action_id, 'success': success, 'impact_score': impact_score}
            )
            
            # Insert results
            if results:
                for key, value in results.items():
                    self.db.execute(
                        """
                        INSERT INTO outcome_results (action_id, key, value)
                        VALUES (%(action_id)s, %(key)s, %(value)s)
                        """,
                        {'action_id': action_id, 'key': key, 'value': str(value)}
                    )
            
            # Anchor the outcome if an anchor client is set
            if self.anchor_client:
                try:
                    result = self.anchor_client.record_outcome(
                        action_id=action_id,
                        outcome_uri=f"ipfs://{action_id}-outcome"  # In a real implementation, we would store actual metadata
                    )
                    
                    # Update outcome with anchoring information
                    self.db.execute(
                        "UPDATE outcomes SET anchored = TRUE, tx_hash = %(tx_hash)s WHERE action_id = %(action_id)s",
                        {'action_id': action_id, 'tx_hash': result.get('tx_hash')}
                    )
                    
                    # Update metrics
                    self.db.execute(
                        "UPDATE metrics SET value = value + 1 WHERE name = 'anchoring_count'"
                    )
                except Exception as e:
                    logger.error(f"Error anchoring outcome: {e}")
            
            return True
        except Exception as e:
            logger.error(f"Error recording outcome: {e}")
            return False


class PostgreSQLReputationSystem:
    """
    PostgreSQL implementation of the Reputation System.
    """
    
    def __init__(self, db=None):
        """
        Initialize the PostgreSQL Reputation System.
        
        Args:
            db: Optional database adapter
        """
        self.db = db or PostgreSQLAdapter()
    
    def update_reputation(self, agent_id, delta, context='global'):
        """
        Update an agent's reputation.
        
        Args:
            agent_id: Agent ID
            delta: Reputation delta
            context: Reputation context
            
        Returns:
            New reputation score
        """
        # Check if agent has a reputation score
        score = self.db.execute(
            """
            SELECT score FROM reputation_scores
            WHERE agent_id = %(agent_id)s AND context = %(context)s
            """,
            {'agent_id': agent_id, 'context': context},
            fetch='one'
        )
        
        if score:
            # Update existing score
            new_score = score['score'] + delta
            self.db.execute(
                """
                UPDATE reputation_scores
                SET score = %(score)s, last_updated = NOW()
                WHERE agent_id = %(agent_id)s AND context = %(context)s
                """,
                {'agent_id': agent_id, 'context': context, 'score': new_score}
            )
        else:
            # Insert new score
            new_score = delta
            self.db.execute(
                """
                INSERT INTO reputation_scores (agent_id, context, score)
                VALUES (%(agent_id)s, %(context)s, %(score)s)
                """,
                {'agent_id': agent_id, 'context': context, 'score': new_score}
            )
        
        return new_score
    
    def get_reputation(self, agent_id, context='global'):
        """
        Get an agent's reputation.
        
        Args:
            agent_id: Agent ID
            context: Reputation context
            
        Returns:
            Reputation score
        """
        score = self.db.execute(
            """
            SELECT score FROM reputation_scores
            WHERE agent_id = %(agent_id)s AND context = %(context)s
            """,
            {'agent_id': agent_id, 'context': context},
            fetch='one'
        )
        
        return score['score'] if score else 0.0
    
    def get_top_agents(self, context='global', limit=10):
        """
        Get the top agents by reputation.
        
        Args:
            context: Reputation context
            limit: Maximum number of agents to return
            
        Returns:
            List of agents with their reputation scores
        """
        results = self.db.execute(
            """
            SELECT a.id, a.name, r.score
            FROM reputation_scores r
            JOIN agents a ON r.agent_id = a.id
            WHERE r.context = %(context)s
            ORDER BY r.score DESC
            LIMIT %(limit)s
            """,
            {'context': context, 'limit': limit},
            fetch='all'
        )
        
        return results 