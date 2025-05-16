"""
JWT Authentication Module

This module provides JWT authentication for the API Gateway.
"""

import os
import time
import jwt
import logging
from typing import Dict, Optional, Annotated
from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Set up logging
logger = logging.getLogger(__name__)

# JWT settings
JWT_SECRET = os.environ.get("JWT_SECRET", "chaoscore_jwt_secret_key")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_MINUTES = int(os.environ.get("JWT_EXPIRATION_MINUTES", "60"))

# Security scheme for Swagger UI
security = HTTPBearer()

def create_jwt_token(agent_id: str, agent_address: Optional[str] = None) -> str:
    """
    Create a JWT token for an agent.
    
    Args:
        agent_id: Agent ID
        agent_address: Ethereum address of the agent (optional)
        
    Returns:
        JWT token
    """
    expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRATION_MINUTES)
    
    payload = {
        "sub": agent_id,
        "exp": expire,
        "iat": datetime.utcnow(),
    }
    
    if agent_address:
        payload["address"] = agent_address
    
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    
    return token

def decode_jwt_token(token: str) -> Dict:
    """
    Decode a JWT token.
    
    Args:
        token: JWT token
        
    Returns:
        Decoded payload
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        
        # Check if token is expired
        if "exp" in payload and payload["exp"] < time.time():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return payload
    except jwt.JWTError as e:
        logger.error(f"JWT decode error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_agent_id(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]) -> str:
    """
    Get the current agent ID from the token.
    
    Args:
        credentials: HTTP authorization credentials
        
    Returns:
        Agent ID
    """
    token = credentials.credentials
    payload = decode_jwt_token(token)
    
    agent_id = payload.get("sub")
    if not agent_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid agent ID in token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return agent_id 