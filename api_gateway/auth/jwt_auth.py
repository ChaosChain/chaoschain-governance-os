"""
JWT Authentication Module

This module provides JWT authentication for the API Gateway.
"""

import os
import time
import uuid
import jwt
import logging
from typing import Dict, Optional, Annotated, List, Set
from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Set up logging
logger = logging.getLogger(__name__)

# JWT settings
JWT_SECRET = os.environ.get("JWT_SECRET", "chaoscore_jwt_secret_key")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_MINUTES = int(os.environ.get("JWT_EXPIRATION_MINUTES", "60"))

# Create a router for JWT-related endpoints
router = APIRouter(prefix="/auth", tags=["Authentication"])

# Security scheme for Swagger UI
security = HTTPBearer()

# Used JTIs (JWT IDs) for replay protection
# In a production system, this would be stored in Redis or a database
used_jtis: Set[str] = set()

# Keys for rotation
jwt_keys = {
    "current": JWT_SECRET,
    "previous": None,
    "next": None,
    "rotation_time": None
}

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
    
    # Create a unique JWT ID (jti) for replay protection
    jti = str(uuid.uuid4())
    
    payload = {
        "sub": agent_id,
        "exp": expire,
        "iat": datetime.utcnow(),
        "jti": jti,  # Add JWT ID for replay protection
    }
    
    if agent_address:
        payload["address"] = agent_address
    
    # Use the current key for signing
    token = jwt.encode(payload, jwt_keys["current"], algorithm=JWT_ALGORITHM)
    
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
        # Try the current key first
        try:
            payload = jwt.decode(token, jwt_keys["current"], algorithms=[JWT_ALGORITHM])
        except jwt.InvalidSignatureError:
            # If that fails, try the previous key if it exists
            if jwt_keys["previous"]:
                payload = jwt.decode(token, jwt_keys["previous"], algorithms=[JWT_ALGORITHM])
            else:
                raise jwt.InvalidSignatureError("Invalid token signature")
        
        # Check if token is expired
        if "exp" in payload and payload["exp"] < time.time():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check for token replay
        if "jti" in payload:
            jti = payload["jti"]
            if jti in used_jtis:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has already been used",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            # Mark this token as used
            used_jtis.add(jti)
            
            # In a production system, we'd also set an expiration on this entry
            # to prevent unbounded memory growth
        
        return payload
    except jwt.InvalidSignatureError as e:
        logger.error(f"JWT signature error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token signature",
            headers={"WWW-Authenticate": "Bearer"},
        )
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

def cleanup_used_jtis():
    """
    Cleanup used JTIs that are past token expiry.
    
    In a production system, this would be handled by Redis TTL or a database job.
    """
    # This is a minimal implementation to prevent memory leaks in the in-memory set
    if len(used_jtis) > 10000:
        logger.warning(f"JTI set size exceeds 10000 ({len(used_jtis)}). Clearing oldest entries.")
        # In reality, we'd only clear expired entries, but this is a simple approach
        # In this simplified version, we'll just clear half the entries
        to_remove = list(used_jtis)[:len(used_jtis) // 2]
        for jti in to_remove:
            used_jtis.remove(jti)

@router.post("/rotate-key", status_code=status.HTTP_200_OK)
async def rotate_jwt_key(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
):
    """
    Rotate the JWT signing key.
    
    This endpoint requires authentication and should only be accessible to admins
    in a real implementation.
    
    Returns:
        Confirmation of key rotation
    """
    # In a production system, we'd check if the agent has admin privileges
    agent_id = get_current_agent_id(credentials)
    
    # Generate a new key
    new_key = str(uuid.uuid4())
    
    # Rotate keys
    jwt_keys["previous"] = jwt_keys["current"]
    jwt_keys["current"] = jwt_keys["next"] if jwt_keys["next"] else new_key
    jwt_keys["next"] = new_key
    jwt_keys["rotation_time"] = datetime.utcnow()
    
    logger.info(f"JWT key rotated by agent {agent_id}")
    
    return {
        "message": "JWT key rotated successfully",
        "rotation_time": jwt_keys["rotation_time"].isoformat()
    }

@router.get("/status", status_code=status.HTTP_200_OK)
async def get_auth_status(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
):
    """
    Get authentication system status.
    
    This endpoint requires authentication and should only be accessible to admins
    in a real implementation.
    
    Returns:
        Authentication system status
    """
    # In a production system, we'd check if the agent has admin privileges
    agent_id = get_current_agent_id(credentials)
    
    # Perform JTI cleanup
    cleanup_used_jtis()
    
    return {
        "status": "operational",
        "used_tokens_count": len(used_jtis),
        "last_key_rotation": jwt_keys["rotation_time"].isoformat() if jwt_keys["rotation_time"] else None,
        "key_states": {
            "current": "active",
            "previous": "active" if jwt_keys["previous"] else "none",
            "next": "prepared" if jwt_keys["next"] else "none"
        }
    } 