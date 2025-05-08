"""
Logger module for ChaosChain Governance OS.

Provides consistent logging across the application with rich formatting.
"""

import logging
import sys
import os
from typing import Optional

# Try to import rich
try:
    from rich.logging import RichHandler
    from rich.console import Console
    HAS_RICH = True
except ImportError:
    HAS_RICH = False


def setup_logger(
    name: str,
    level: Optional[str] = None,
    verbose: bool = False
) -> logging.Logger:
    """
    Set up a logger with optional rich formatting.
    
    Args:
        name: Logger name
        level: Logging level (overrides environment variable and verbose flag)
        verbose: Whether to use DEBUG level
        
    Returns:
        Configured logger
    """
    # Determine log level
    if level is None:
        level = os.environ.get("LOG_LEVEL", "INFO")
        if verbose:
            level = "DEBUG"
    
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    # Configure logger
    if HAS_RICH:
        console = Console(stderr=True)
        logging.basicConfig(
            level=numeric_level,
            format="%(message)s",
            datefmt="[%X]",
            handlers=[RichHandler(
                console=console,
                rich_tracebacks=True,
                markup=True,
                show_time=True,
                show_path=True
            )]
        )
    else:
        logging.basicConfig(
            level=numeric_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.StreamHandler(sys.stdout)]
        )
    
    logger = logging.getLogger(name)
    logger.setLevel(numeric_level)
    
    if HAS_RICH:
        logger.info(f"Rich logging enabled for [bold]{name}[/bold]")
    else:
        logger.info(f"Standard logging enabled for {name}")
    
    return logger


def get_logger(
    name: str,
    level: Optional[str] = None,
    verbose: bool = False
) -> logging.Logger:
    """
    Get a logger with the specified name.
    
    Args:
        name: Logger name
        level: Logging level
        verbose: Whether to use DEBUG level
        
    Returns:
        Logger instance
    """
    return setup_logger(name, level, verbose) 