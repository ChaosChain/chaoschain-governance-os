"""
Agent runtime runner for the ChaosChain platform.
Manages the execution of agent workloads.
"""

import asyncio
import logging
import os
import sys
from typing import Any, Dict, List, Optional, Union

# Add the parent directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from utils import get_logger

# Check if streaming is enabled
ENABLE_STREAM = os.environ.get("ENABLE_STREAM", "0") == "1"

# Import stream router if streaming is enabled
if ENABLE_STREAM:
    try:
        from api.rest.routers.stream import add_log
        logger = get_logger("agent.runtime.runner", stream_handler=True)
    except ImportError:
        logger = get_logger("agent.runtime.runner")
        logger.warning("Stream module not found, disabling streaming")
        ENABLE_STREAM = False
else:
    logger = get_logger("agent.runtime.runner")

class LogHandler(logging.Handler):
    """
    Custom logging handler that forwards logs to the streaming endpoint.
    """
    def __init__(self):
        super().__init__()
        self.loop = asyncio.get_event_loop_policy().get_event_loop()
        
    def emit(self, record):
        """
        Process a log record by sending it to the streaming endpoint.
        """
        try:
            # Extract agent name from the logger name if possible
            agent = record.name.split('.')[-1] if '.' in record.name else "system"
            
            # Format the message
            msg = self.format(record)
            
            # Schedule the coroutine to run in the event loop
            if ENABLE_STREAM:
                asyncio.run_coroutine_threadsafe(
                    add_log(agent, record.levelname.lower(), msg),
                    self.loop
                )
        except Exception:
            self.handleError(record)

# Add the custom handler if streaming is enabled
if ENABLE_STREAM:
    handler = LogHandler()
    handler.setLevel(logging.INFO)
    logger.addHandler(handler)
    logger.info("Log streaming enabled")

class AgentRunner:
    """
    Manages the lifecycle of agent execution.
    """
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logger
        
    async def run(self, agent_class, **kwargs):
        """
        Run an agent with the specified parameters.
        """
        self.logger.info(f"Starting agent: {agent_class.__name__}")
        
        # Log to stream if enabled
        if ENABLE_STREAM:
            await add_log(
                agent_class.__name__, 
                "info", 
                f"Agent {agent_class.__name__} starting"
            )
            
        try:
            agent = agent_class(**kwargs)
            result = await agent.execute()
            
            self.logger.info(f"Agent {agent_class.__name__} completed successfully")
            
            # Log to stream if enabled
            if ENABLE_STREAM:
                await add_log(
                    agent_class.__name__,
                    "info",
                    f"Agent {agent_class.__name__} completed successfully"
                )
                
            return result
            
        except Exception as e:
            self.logger.error(f"Agent {agent_class.__name__} failed: {str(e)}")
            
            # Log to stream if enabled
            if ENABLE_STREAM:
                await add_log(
                    agent_class.__name__,
                    "error",
                    f"Agent {agent_class.__name__} failed: {str(e)}"
                )
                
            raise 