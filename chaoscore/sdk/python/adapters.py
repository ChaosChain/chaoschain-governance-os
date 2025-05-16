"""
ChaosCore Adapters

This module provides adapters for integrating ChaosCore with other systems and frameworks.
"""
from typing import Dict, Any, Optional, List, Callable
import logging

try:
    from crewai import Agent, Crew, Task
    HAS_CREWAI = True
except ImportError:
    HAS_CREWAI = False

logger = logging.getLogger(__name__)


class CrewAIAdapter:
    """
    Adapter for integrating ChaosCore with CrewAI.
    """
    
    def __init__(self, chaoscore_client):
        """
        Initialize the CrewAI adapter.
        
        Args:
            chaoscore_client: ChaosCore client instance
        """
        if not HAS_CREWAI:
            raise ImportError(
                "CrewAI is required for using CrewAIAdapter. "
                "Install it with 'pip install crewai'."
            )
        
        self.client = chaoscore_client
        self.agent_map = {}  # Map CrewAI agent names to ChaosCore agent IDs
    
    def register_agent(self, agent: 'Agent') -> str:
        """
        Register a CrewAI agent with ChaosCore.
        
        Args:
            agent: CrewAI agent
            
        Returns:
            ChaosCore agent ID
        """
        # Extract metadata from the agent
        metadata = {
            "role": agent.role,
            "goal": agent.goal,
            "backstory": agent.backstory,
            "llm": str(agent.llm) if agent.llm else None,
            "is_crewai_agent": True
        }
        
        # Register the agent with ChaosCore
        agent_id = self.client.register_agent(
            name=agent.role,
            email=f"{agent.role.lower().replace(' ', '-')}@chaoscore.ai",
            metadata=metadata
        )
        
        # Store the mapping
        self.agent_map[agent.role] = agent_id
        
        return agent_id
    
    def get_agent_id(self, agent: 'Agent') -> Optional[str]:
        """
        Get the ChaosCore agent ID for a CrewAI agent.
        
        Args:
            agent: CrewAI agent
            
        Returns:
            ChaosCore agent ID, or None if not registered
        """
        return self.agent_map.get(agent.role)
    
    def wrap_task(self, task: 'Task', agent: 'Agent') -> Callable:
        """
        Wrap a CrewAI task execution to log it with ChaosCore.
        
        Args:
            task: CrewAI task
            agent: CrewAI agent
            
        Returns:
            Wrapped task execution function
        """
        original_execution = task._execution
        agent_id = self.get_agent_id(agent)
        
        if not agent_id:
            agent_id = self.register_agent(agent)
        
        def wrapped_execution(*args, **kwargs):
            # Log the task start
            action_id = self.client.log_action(
                agent_id=agent_id,
                action_type="EXECUTE_TASK",
                description=f"Execute task: {task.description[:100]}...",
                data={
                    "task_description": task.description,
                    "expected_output": task.expected_output,
                    "context": [str(c) for c in task.context] if task.context else []
                }
            )
            
            try:
                # Execute the original task
                result = original_execution(*args, **kwargs)
                
                # Record successful outcome
                self.client.record_outcome(
                    action_id=action_id,
                    success=True,
                    results={"output": result},
                    impact_score=0.7
                )
                
                return result
            except Exception as e:
                # Record failed outcome
                self.client.record_outcome(
                    action_id=action_id,
                    success=False,
                    results={"error": str(e)},
                    impact_score=0.0
                )
                
                # Re-raise the exception
                raise
        
        # Replace the task execution function
        task._execution = wrapped_execution
        
        return wrapped_execution
    
    def adapt_crew(self, crew: 'Crew') -> 'Crew':
        """
        Adapt a CrewAI crew to integrate with ChaosCore.
        
        Args:
            crew: CrewAI crew
            
        Returns:
            Adapted CrewAI crew
        """
        # Register all agents
        for agent in crew.agents:
            if self.get_agent_id(agent) is None:
                self.register_agent(agent)
        
        # Wrap all tasks
        for task in crew.tasks:
            self.wrap_task(task, task.agent)
        
        # Return the modified crew
        return crew
    
    def run_crew(self, crew: 'Crew') -> Dict[str, Any]:
        """
        Run a CrewAI crew with ChaosCore integration.
        
        Args:
            crew: CrewAI crew
            
        Returns:
            Dictionary with results and ChaosCore action IDs
        """
        # Adapt the crew
        adapted_crew = self.adapt_crew(crew)
        
        # Run the crew
        results = adapted_crew.kickoff()
        
        # Return the results
        return {
            "results": results,
            "agent_ids": self.agent_map
        } 