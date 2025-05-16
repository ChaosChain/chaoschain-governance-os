"""
API Gateway Dependencies

This module provides dependency injection for the API Gateway.
"""

import os
import logging
from typing import Annotated, Optional

from fastapi import Depends, HTTPException, status

# Import database adapters
from chaoscore.core.database_adapter import PostgreSQLAdapter
from api_gateway.testing.sqlite_adapter import SQLiteAdapter

logger = logging.getLogger(__name__)

# Database adapter cached instance
_db_adapter = None

def get_db_adapter():
    """
    Factory function for database adapter dependency.
    
    This function returns a singleton database adapter instance.
    In test mode, it can be overridden to return a SQLiteAdapter.
    
    Returns:
        Database adapter instance
    """
    global _db_adapter
    
    # Check if we already have an adapter
    if _db_adapter is not None:
        return _db_adapter
    
    # Check if we're in test mode
    if os.environ.get("SQLITE_TEST_MODE") == "true":
        # Use SQLite adapter for testing
        try:
            logger.info("Creating SQLite adapter for testing")
            _db_adapter = SQLiteAdapter()
            
            # Test the connection
            _db_adapter.connect()
            
            return _db_adapter
        except Exception as e:
            logger.error(f"Failed to create SQLite adapter: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Test database connection failed"
            )
    else:
        # Create a PostgreSQL adapter
        try:
            logger.info("Creating PostgreSQL adapter")
            _db_adapter = PostgreSQLAdapter()
            
            # Test the connection
            _db_adapter.connect()
            
            return _db_adapter
        except Exception as e:
            logger.error(f"Failed to create PostgreSQL adapter: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database connection failed"
            )
    
    # In case of no adapter (should not happen)
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="No database adapter available"
    ) 