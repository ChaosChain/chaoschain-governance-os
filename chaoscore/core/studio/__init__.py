"""
Studio module for ChaosCore.

This module provides interfaces and implementations for Studios.
"""

import json
import uuid
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime


class StudioManager(ABC):
    """Interface for Studio Manager implementations."""

    @abstractmethod
    def create_studio(self, name: str, description: str, owner_id: str, members: Optional[List[Dict[str, Any]]] = None, settings: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a new studio.
        
        Args:
            name: Studio name
            description: Studio description
            owner_id: Owner agent ID
            members: Studio members
            settings: Studio settings
            
        Returns:
            Studio ID
        """
        pass

    @abstractmethod
    def get_studio(self, studio_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a studio by ID.
        
        Args:
            studio_id: Studio ID
            
        Returns:
            Studio data or None if not found
        """
        pass

    @abstractmethod
    def list_studios(self, owner_id: Optional[str] = None, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        List studios.
        
        Args:
            owner_id: Filter by owner ID
            limit: Maximum number of studios to return
            offset: Offset for pagination
            
        Returns:
            List of studios
        """
        pass

    @abstractmethod
    def add_studio_member(self, studio_id: str, agent_id: str, role: str, permissions: Optional[List[str]] = None) -> bool:
        """
        Add a member to a studio.
        
        Args:
            studio_id: Studio ID
            agent_id: Agent ID
            role: Member role
            permissions: Member permissions
            
        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    def remove_studio_member(self, studio_id: str, agent_id: str) -> bool:
        """
        Remove a member from a studio.
        
        Args:
            studio_id: Studio ID
            agent_id: Agent ID
            
        Returns:
            True if successful, False otherwise
        """
        pass


class InMemoryStudioManager(StudioManager):
    """In-memory implementation of Studio Manager."""

    def __init__(self):
        """Initialize the in-memory studio manager."""
        self.studios = {}
        self.members = {}

    def create_studio(self, name: str, description: str, owner_id: str, members: Optional[List[Dict[str, Any]]] = None, settings: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a new studio.
        
        Args:
            name: Studio name
            description: Studio description
            owner_id: Owner agent ID
            members: Studio members
            settings: Studio settings
            
        Returns:
            Studio ID
        """
        studio_id = f"studio-{uuid.uuid4()}"
        created_at = datetime.utcnow().isoformat()
        
        self.studios[studio_id] = {
            "id": studio_id,
            "name": name,
            "description": description,
            "owner_id": owner_id,
            "created_at": created_at,
            "settings": settings or {}
        }
        
        # Add members
        self.members[studio_id] = []
        
        if members:
            for member in members:
                self.add_studio_member(
                    studio_id=studio_id,
                    agent_id=member["agent_id"],
                    role=member["role"],
                    permissions=member.get("permissions", [])
                )
        
        return studio_id

    def get_studio(self, studio_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a studio by ID.
        
        Args:
            studio_id: Studio ID
            
        Returns:
            Studio data or None if not found
        """
        if studio_id not in self.studios:
            return None
        
        studio = self.studios[studio_id].copy()
        studio["members"] = self.members.get(studio_id, [])
        
        return studio

    def list_studios(self, owner_id: Optional[str] = None, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        List studios.
        
        Args:
            owner_id: Filter by owner ID
            limit: Maximum number of studios to return
            offset: Offset for pagination
            
        Returns:
            List of studios
        """
        studios = list(self.studios.values())
        
        if owner_id:
            studios = [s for s in studios if s["owner_id"] == owner_id]
        
        studios.sort(key=lambda s: s["created_at"], reverse=True)
        
        return studios[offset:offset+limit]

    def add_studio_member(self, studio_id: str, agent_id: str, role: str, permissions: Optional[List[str]] = None) -> bool:
        """
        Add a member to a studio.
        
        Args:
            studio_id: Studio ID
            agent_id: Agent ID
            role: Member role
            permissions: Member permissions
            
        Returns:
            True if successful, False otherwise
        """
        if studio_id not in self.studios:
            return False
        
        if studio_id not in self.members:
            self.members[studio_id] = []
        
        # Remove if already exists
        self.members[studio_id] = [m for m in self.members[studio_id] if m["agent_id"] != agent_id]
        
        # Add new member
        self.members[studio_id].append({
            "agent_id": agent_id,
            "role": role,
            "permissions": permissions or [],
            "joined_at": datetime.utcnow().isoformat()
        })
        
        return True

    def remove_studio_member(self, studio_id: str, agent_id: str) -> bool:
        """
        Remove a member from a studio.
        
        Args:
            studio_id: Studio ID
            agent_id: Agent ID
            
        Returns:
            True if successful, False otherwise
        """
        if studio_id not in self.studios or studio_id not in self.members:
            return False
        
        original_count = len(self.members[studio_id])
        self.members[studio_id] = [m for m in self.members[studio_id] if m["agent_id"] != agent_id]
        
        return len(self.members[studio_id]) < original_count


__all__ = ["StudioManager", "InMemoryStudioManager"] 