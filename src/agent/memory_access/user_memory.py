"""
User memory management module for storing and retrieving user information.
"""

from typing import Dict, List, Optional, Tuple, Union
import json
from datetime import datetime
from pathlib import Path
import glob
import os
from config.settings import settings

class UserMemory:
    """Class for managing user memories and preferences."""
    
    def __init__(self, storage_dir: str = settings.USERS_MEMORY_PATH):
        """Initialize UserMemory with storage directory."""
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.temp_user_counter = 0
        
    def get_user_context(self, user_id: str) -> Dict:
        """Get user context for specified user.
        
        Args:
            user_id: User ID to get context for
            
        Returns:
            Dict containing user context information
        """
        if not user_id or user_id == "anonymous":
            return {}
            
        # Load memories for user
        memory_file = self.storage_dir / f"{user_id}.json"
        if memory_file.exists():
            with open(memory_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}
        
    def update_memory(self, memory_type: str, data: Union[Dict, List], user_id: Optional[str] = None) -> None:
        """Update user memory with new information.
        
        Args:
            memory_type: Type of memory to update (basic_info/preferences/relationships/aliases)
            data: New data to incorporate
            user_id: Optional user ID to update (defaults to current user)
        """
        if not user_id or user_id == "anonymous":
            return
            
        # Load existing memories
        memory_file = self.storage_dir / f"{user_id}.json"
        if memory_file.exists():
            with open(memory_file, "r", encoding="utf-8") as f:
                memories = json.load(f)
        else:
            memories = {
                "user_id": user_id,
                "basic_info": {},
                "preferences": {},
                "relationships": {},
                "aliases": [],  # List of alternative names used to refer to this user
                "interactions": [],
                "is_temporary": user_id.startswith("temp_")
            }
            
        # Update memories
        if memory_type not in memories:
            memories[memory_type] = {} if memory_type != "aliases" else []
            
        if memory_type == "aliases":
            # For aliases, ensure uniqueness and append new ones
            current_aliases = set(memories["aliases"])
            if isinstance(data, dict) and "names" in data:
                current_aliases.update(data["names"])
            elif isinstance(data, list):
                current_aliases.update(data)
            memories["aliases"] = list(current_aliases)
        elif memory_type == "basic_info" and "voice_samples" in data:
            # Special handling for voice samples to ensure they're stored as a list
            if "voice_samples" not in memories["basic_info"]:
                memories["basic_info"]["voice_samples"] = []
            if isinstance(data["voice_samples"], list):
                memories["basic_info"]["voice_samples"] = data["voice_samples"]
            else:
                memories["basic_info"]["voice_samples"].append(data["voice_samples"])
            # Update other basic info fields
            for key, value in data.items():
                if key != "voice_samples":
                    memories["basic_info"][key] = value
        elif isinstance(data, dict):
            # For dict, update existing data
            if memory_type not in memories:
                memories[memory_type] = {}
            memories[memory_type].update(data)
        elif isinstance(data, list):
            # For list, append new items
            if memory_type not in memories:
                memories[memory_type] = []
            memories[memory_type].extend(data)
        else:
            # For other types, replace
            memories[memory_type] = data
        
        # Save memories
        with open(memory_file, "w", encoding="utf-8") as f:
            json.dump(memories, f, ensure_ascii=False, indent=2)
        
    def add_interaction(self, interaction_type: str, content: Dict, user_id: Optional[str] = None) -> None:
        """Add new interaction to user's history.
        
        Args:
            interaction_type: Type of interaction
            content: Content of the interaction
            user_id: Optional user ID to update (defaults to current user)
        """
        if not user_id or user_id == "anonymous":
            return
            
        # Load existing memories
        memory_file = self.storage_dir / f"{user_id}.json"
        if memory_file.exists():
            with open(memory_file, "r", encoding="utf-8") as f:
                memories = json.load(f)
        else:
            memories = {
                "user_id": user_id,
                "basic_info": {},
                "preferences": {},
                "relationships": {},
                "aliases": [],
                "interactions": [],
                "is_temporary": user_id.startswith("temp_")
            }
            
        # Add interaction
        if "interactions" not in memories:
            memories["interactions"] = []
            
        memories["interactions"].append({
            "timestamp": datetime.now().isoformat(),
            "type": interaction_type,
            "content": content
        })
        
        # Save memories
        with open(memory_file, "w", encoding="utf-8") as f:
            json.dump(memories, f, ensure_ascii=False, indent=2)
            
    def find_user_by_voice(self, voice_id: str) -> Tuple[Optional[str], bool]:
        """Find user ID by voice ID.
        
        Args:
            voice_id: Voice identifier to search for
            
        Returns:
            Tuple of (user_id, is_temporary) if found, (None, False) otherwise
        """
        # Search all memory files
        for memory_file in glob.glob(str(self.storage_dir / "*.json")):
            try:
                with open(memory_file, "r", encoding="utf-8") as f:
                    memories = json.load(f)
                    if memories.get("basic_info", {}).get("voice_id") == voice_id:
                        return memories["user_id"], memories.get("is_temporary", False)
            except Exception:
                continue
        return None, False
        
    def find_user_by_alias(self, alias: str, current_user_id: Optional[str] = None) -> Optional[str]:
        """Find user ID by alias or name.
        
        Args:
            alias: Alias or name to search for
            current_user_id: Optional current user ID to check relationships
            
        Returns:
            User ID if found, None otherwise
        """
        alias = alias.lower()
        
        # First check relationships of current user if provided
        if current_user_id:
            current_user = self.get_user_context(current_user_id)
            if partner_id := current_user.get("relationships", {}).get("partner"):
                partner = self.get_user_context(partner_id)
                # Check partner's aliases and name
                if alias in [n.lower() for n in partner.get("aliases", [])]:
                    return partner_id
                if partner.get("basic_info", {}).get("name", "").lower() == alias:
                    return partner_id
                    
        # Search all memory files
        for memory_file in glob.glob(str(self.storage_dir / "*.json")):
            try:
                with open(memory_file, "r", encoding="utf-8") as f:
                    memories = json.load(f)
                    # Check aliases
                    if alias in [n.lower() for n in memories.get("aliases", [])]:
                        return memories["user_id"]
                    # Check name
                    if memories.get("basic_info", {}).get("name", "").lower() == alias:
                        return memories["user_id"]
            except Exception:
                continue
        return None
        
    def create_temporary_user(self, initial_data: Optional[Dict] = None) -> str:
        """Create a temporary user entry.
        
        Args:
            initial_data: Optional initial data for the user
            
        Returns:
            Temporary user ID
        """
        self.temp_user_counter += 1
        temp_user_id = f"temp_{self.temp_user_counter}"
        
        # Create memory file with initial data
        memories = {
            "user_id": temp_user_id,
            "basic_info": {},
            "preferences": {},
            "relationships": {},
            "aliases": [],
            "interactions": [],
            "is_temporary": True
        }
        
        if initial_data:
            for key, value in initial_data.items():
                if key in memories:
                    memories[key] = value
                    
        # Save memories
        memory_file = self.storage_dir / f"{temp_user_id}.json"
        with open(memory_file, "w", encoding="utf-8") as f:
            json.dump(memories, f, ensure_ascii=False, indent=2)
            
        return temp_user_id
        
    def merge_users(self, source_id: str, target_id: str) -> None:
        """Merge two user records, typically when a temporary user is identified.
        
        Args:
            source_id: User ID to merge from (typically temporary)
            target_id: User ID to merge into
        """
        # Load source memories
        source_file = self.storage_dir / f"{source_id}.json"
        if not source_file.exists():
            return
            
        with open(source_file, "r", encoding="utf-8") as f:
            source_memories = json.load(f)
            
        # Load target memories
        target_file = self.storage_dir / f"{target_id}.json"
        if target_file.exists():
            with open(target_file, "r", encoding="utf-8") as f:
                target_memories = json.load(f)
        else:
            target_memories = {
                "user_id": target_id,
                "basic_info": {},
                "preferences": {},
                "relationships": {},
                "aliases": [],
                "interactions": [],
                "is_temporary": False
            }
            
        # Merge memories
        for key in ["basic_info", "preferences", "relationships"]:
            if isinstance(source_memories.get(key), dict):
                target_memories[key].update(source_memories[key])
            elif isinstance(source_memories.get(key), list):
                target_memories[key].extend(source_memories[key])
                
        # Merge aliases
        if "aliases" in source_memories:
            current_aliases = set(target_memories.get("aliases", []))
            current_aliases.update(source_memories["aliases"])
            target_memories["aliases"] = list(current_aliases)
                
        # Merge interactions
        target_memories["interactions"].extend(source_memories["interactions"])
        
        # Save merged memories
        with open(target_file, "w", encoding="utf-8") as f:
            json.dump(target_memories, f, ensure_ascii=False, indent=2)
            
        # Delete source file
        source_file.unlink()

# Global instance
user_memory = UserMemory()
