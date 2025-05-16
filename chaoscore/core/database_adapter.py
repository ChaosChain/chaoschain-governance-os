"""
Database Adapter Interfaces

This module provides interfaces for database adapters used by the ChaosCore platform.
For demonstration purposes in the API Gateway integration tests.
"""

import logging
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional

class BaseAdapter:
    """Base adapter interface."""
    
    def connect(self):
        """Connect to the database."""
        raise NotImplementedError

class PostgreSQLAdapter(BaseAdapter):
    """
    PostgreSQL adapter for the ChaosCore platform.
    
    This is a mock implementation for demonstration purposes.
    """
    
    def __init__(self):
        """Initialize the PostgreSQL adapter."""
        self.agents = {}
        self.actions = {}
        self.outcomes = {}
        self.studios = {}
        self.tasks = {}
        self.reputation = {}
    
    def connect(self):
        """Connect to the PostgreSQL database."""
        logging.info("Connected to PostgreSQL database")
        return True
    
    # --- Agent Registry Methods ---
    
    def register_agent(self, name, email, metadata=None):
        """Register a new agent."""
        agent_id = f"agent-{uuid.uuid4()}"
        registration_time = datetime.now()
        
        self.agents[agent_id] = {
            "id": agent_id,
            "name": name,
            "email": email,
            "metadata": metadata or {},
            "registration_time": registration_time
        }
        
        return agent_id
    
    def get_agent(self, agent_id):
        """Get agent by ID."""
        if agent_id not in self.agents:
            return None
        
        agent_data = self.agents[agent_id]
        
        class Agent:
            def __init__(self, data):
                self.data = data
            
            def get_id(self):
                return self.data["id"]
            
            def get_name(self):
                return self.data["name"]
            
            def get_email(self):
                return self.data["email"]
            
            def get_metadata(self):
                return self.data["metadata"]
            
            def get_registration_time(self):
                return self.data["registration_time"]
        
        return Agent(agent_data)
    
    def list_agents(self, limit=10, offset=0):
        """List agents with pagination."""
        agent_list = list(self.agents.values())[offset:offset+limit]
        
        result = []
        for agent_data in agent_list:
            class Agent:
                def __init__(self, data):
                    self.data = data
                
                def get_id(self):
                    return self.data["id"]
                
                def get_name(self):
                    return self.data["name"]
                
                def get_email(self):
                    return self.data["email"]
                
                def get_metadata(self):
                    return self.data["metadata"]
                
                def get_registration_time(self):
                    return self.data["registration_time"]
            
            result.append(Agent(agent_data))
        
        return result
    
    # --- Action Methods ---
    
    def log_action(self, agent_id, action_type, description, data=None):
        """Log an action."""
        action_id = f"action-{uuid.uuid4()}"
        timestamp = datetime.now()
        
        self.actions[action_id] = {
            "id": action_id,
            "agent_id": agent_id,
            "action_type": action_type,
            "description": description,
            "data": data or {},
            "timestamp": timestamp
        }
        
        return action_id
    
    def record_outcome(self, action_id, success, results=None, impact_score=0.0):
        """Record the outcome of an action."""
        if action_id not in self.actions:
            return False
        
        timestamp = datetime.now()
        
        self.outcomes[action_id] = {
            "action_id": action_id,
            "success": success,
            "results": results or {},
            "impact_score": impact_score,
            "timestamp": timestamp
        }
        
        # Update reputation for the agent
        agent_id = self.actions[action_id]["agent_id"]
        self._update_reputation(agent_id, impact_score if success else -impact_score)
        
        return True
    
    # --- Studio Methods ---
    
    def create_studio(self, name, description, owner_id, metadata=None):
        """Create a new studio."""
        studio_id = f"studio-{uuid.uuid4()}"
        created_at = datetime.now()
        
        self.studios[studio_id] = {
            "id": studio_id,
            "name": name,
            "description": description,
            "owner_id": owner_id,
            "metadata": metadata or {},
            "created_at": created_at
        }
        
        return studio_id
    
    def get_studio(self, studio_id):
        """Get a studio by ID."""
        if studio_id not in self.studios:
            return None
        
        studio_data = self.studios[studio_id]
        
        class Studio:
            def __init__(self, data):
                self.data = data
            
            def get_id(self):
                return self.data["id"]
            
            def get_name(self):
                return self.data["name"]
            
            def get_description(self):
                return self.data["description"]
            
            def get_owner_id(self):
                return self.data["owner_id"]
            
            def get_metadata(self):
                return self.data["metadata"]
            
            def get_created_at(self):
                return self.data["created_at"]
        
        return Studio(studio_data)
    
    def list_studios(self, limit=10, offset=0):
        """List studios with pagination."""
        studio_list = list(self.studios.values())[offset:offset+limit]
        
        result = []
        for studio_data in studio_list:
            class Studio:
                def __init__(self, data):
                    self.data = data
                
                def get_id(self):
                    return self.data["id"]
                
                def get_name(self):
                    return self.data["name"]
                
                def get_description(self):
                    return self.data["description"]
                
                def get_owner_id(self):
                    return self.data["owner_id"]
                
                def get_metadata(self):
                    return self.data["metadata"]
                
                def get_created_at(self):
                    return self.data["created_at"]
            
            result.append(Studio(studio_data))
        
        return result
    
    def create_task(self, studio_id, name, description, parameters=None):
        """Create a new task."""
        if studio_id not in self.studios:
            return None
        
        task_id = f"task-{uuid.uuid4()}"
        created_at = datetime.now()
        updated_at = created_at
        
        self.tasks[task_id] = {
            "id": task_id,
            "studio_id": studio_id,
            "name": name,
            "description": description,
            "parameters": parameters or {},
            "status": "PENDING",
            "created_at": created_at,
            "updated_at": updated_at
        }
        
        return task_id
    
    def get_task(self, task_id):
        """Get a task by ID."""
        if task_id not in self.tasks:
            return None
        
        task_data = self.tasks[task_id]
        
        class Task:
            def __init__(self, data):
                self.data = data
            
            def get_id(self):
                return self.data["id"]
            
            def get_studio_id(self):
                return self.data["studio_id"]
            
            def get_name(self):
                return self.data["name"]
            
            def get_description(self):
                return self.data["description"]
            
            def get_parameters(self):
                return self.data["parameters"]
            
            def get_status(self):
                return self.data["status"]
            
            def get_created_at(self):
                return self.data["created_at"]
            
            def get_updated_at(self):
                return self.data["updated_at"]
        
        return Task(task_data)
    
    # --- Reputation Methods ---
    
    def _update_reputation(self, agent_id, delta):
        """Update agent reputation."""
        if agent_id not in self.agents:
            return
        
        if agent_id not in self.reputation:
            self.reputation[agent_id] = {
                "agent_id": agent_id,
                "score": 0.0,
                "rank": None,
                "components": {},
                "last_updated": datetime.now()
            }
        
        self.reputation[agent_id]["score"] += delta
        self.reputation[agent_id]["last_updated"] = datetime.now()
        
        # Update ranks
        sorted_agents = sorted(
            self.reputation.values(),
            key=lambda x: x["score"],
            reverse=True
        )
        
        for i, agent in enumerate(sorted_agents):
            agent["rank"] = i + 1
    
    def get_agent_reputation(self, agent_id):
        """Get reputation for an agent."""
        if agent_id not in self.reputation:
            return None
        
        reputation_data = self.reputation[agent_id]
        
        class Reputation:
            def __init__(self, data):
                self.data = data
            
            def get_agent_id(self):
                return self.data["agent_id"]
            
            def get_score(self):
                return self.data["score"]
            
            def get_rank(self):
                return self.data["rank"]
            
            def get_components(self):
                return self.data["components"]
            
            def get_last_updated(self):
                return self.data["last_updated"]
        
        return Reputation(reputation_data)
    
    def list_agent_reputations(self, limit=10, offset=0, min_score=None, domain=None):
        """List agent reputations with pagination and filtering."""
        filtered_reputations = self.reputation.values()
        
        if min_score is not None:
            filtered_reputations = [r for r in filtered_reputations if r["score"] >= min_score]
        
        # Domain filtering not implemented for this mock
        
        sorted_reputations = sorted(
            filtered_reputations,
            key=lambda x: x["score"],
            reverse=True
        )
        
        paginated_reputations = sorted_reputations[offset:offset+limit]
        
        result = []
        for reputation_data in paginated_reputations:
            class Reputation:
                def __init__(self, data):
                    self.data = data
                
                def get_agent_id(self):
                    return self.data["agent_id"]
                
                def get_score(self):
                    return self.data["score"]
                
                def get_rank(self):
                    return self.data["rank"]
                
                def get_components(self):
                    return self.data["components"]
                
                def get_last_updated(self):
                    return self.data["last_updated"]
            
            result.append(Reputation(reputation_data))
        
        return result
    
    def get_domain_reputation_leaderboard(self, domain, limit=10, offset=0):
        """Get reputation leaderboard for a specific domain."""
        # Domain filtering not implemented for this mock
        return self.list_agent_reputations(limit=limit, offset=offset) 