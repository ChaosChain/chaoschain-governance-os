"""
API key authentication middleware.
"""

import os
from typing import List, Optional
from fastapi import Security, HTTPException, Depends
from fastapi.security.api_key import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API keys from environment
API_KEYS = os.getenv("API_KEYS", "test_key").split(",")

# API key header
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def get_api_key(api_key_header: str = Security(api_key_header)) -> str:
    """
    Validate API key.
    
    Args:
        api_key_header: API key from request header
        
    Returns:
        API key if valid
        
    Raises:
        HTTPException: If API key is invalid
    """
    if not api_key_header:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Missing API key"
        )
        
    if api_key_header not in API_KEYS:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Invalid API key"
        )
        
    return api_key_header 