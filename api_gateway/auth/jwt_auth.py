"""
JWT Authentication for ChaosCore API Gateway

This module provides JWT authentication for the ChaosCore API Gateway.
It uses agent private keys to sign tokens and verifies them using the agent's public key
retrieved from the AgentRegistry.
"""
import os
import time
import json
from typing import Dict, Optional, Any
import jwt
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.status import HTTP_401_UNAUTHORIZED

from chaoscore.core.agent_registry import AgentRegistryInterface

# JWT settings
JWT_SECRET = os.environ.get("JWT_SECRET", "chaoscore-secret-key")
JWT_ALGORITHM = "RS256"
JWT_EXPIRATION = 3600  # 1 hour

# Security scheme
security = HTTPBearer()


class JWTAuth:
    """
    JWT Authentication handler for ChaosCore API Gateway.
    """
    
    def __init__(self, agent_registry: AgentRegistryInterface):
        """
        Initialize the JWT authentication handler.
        
        Args:
            agent_registry: AgentRegistry instance for validating agent keys
        """
        self.agent_registry = agent_registry
    
    def create_token(self, agent_id: str, private_key: str, additional_claims: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a JWT token signed by the agent's private key.
        
        Args:
            agent_id: Agent ID
            private_key: Agent's private key in PEM format
            additional_claims: Additional claims to include in the token
            
        Returns:
            JWT token
        """
        payload = {
            "sub": agent_id,
            "exp": time.time() + JWT_EXPIRATION,
            "iat": time.time(),
            **(additional_claims or {})
        }
        
        # Create the token with the agent_id as the key ID (kid) header
        token = jwt.encode(
            payload=payload,
            key=private_key,
            algorithm=JWT_ALGORITHM,
            headers={"kid": agent_id}
        )
        
        return token
    
    async def get_current_agent(self, credentials: HTTPAuthorizationCredentials = Security(security)) -> Dict[str, Any]:
        """
        Get the current agent from the JWT token.
        
        Args:
            credentials: HTTP Authorization credentials
            
        Returns:
            Agent information
            
        Raises:
            HTTPException: If the token is invalid
        """
        try:
            # Extract the token
            token = credentials.credentials
            
            # Decode the token headers without verification to get the agent_id
            unverified_headers = jwt.get_unverified_header(token)
            agent_id = unverified_headers.get("kid")
            
            if not agent_id:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: missing agent ID in headers"
                )
            
            # Get the agent from the registry
            agent = self.agent_registry.get_agent(agent_id)
            
            if not agent:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail=f"Agent not found: {agent_id}"
                )
            
            # Get the agent's public key from metadata
            metadata = agent.get("metadata", {}) if isinstance(agent, dict) else {}
            
            # Ensure metadata is a dictionary
            if isinstance(metadata, str):
                try:
                    metadata = json.loads(metadata)
                except (json.JSONDecodeError, TypeError):
                    metadata = {}
            
            public_key = metadata.get("public_key")
            
            if not public_key:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail=f"Agent {agent_id} has no public key registered"
                )
            
            # Verify the token
            payload = jwt.decode(
                token,
                public_key,
                algorithms=[JWT_ALGORITHM],
                options={"verify_signature": True}
            )
            
            # Check if the token subject matches the agent ID
            if payload["sub"] != agent_id:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="Token subject does not match agent ID"
                )
            
            # Return the agent information
            return {
                "agent_id": agent_id,
                "name": agent.get("name") if isinstance(agent, dict) else agent.get_name(),
                "email": agent.get("email") if isinstance(agent, dict) else agent.get_email(),
                "metadata": metadata
            }
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.JWTError as e:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail=f"Authentication error: {str(e)}"
            )
    
    # Dependency for protected routes
    async def requires_auth(self, credentials: HTTPAuthorizationCredentials = Security(security)) -> Dict[str, Any]:
        """
        Dependency for protected routes that require authentication.
        
        Args:
            credentials: HTTP Authorization credentials
            
        Returns:
            Agent information
        """
        return await self.get_current_agent(credentials) 