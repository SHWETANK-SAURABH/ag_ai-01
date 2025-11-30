"""Memory store for conversation and context management."""

from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class MemoryStore:
    """Store for managing conversation history and context."""
    
    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or Path("memory/storage/memory.json")
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.conversations: List[Dict[str, Any]] = []
        self.context: Dict[str, Any] = {}
        
        self._load()
    
    def add_conversation_turn(self, user_input: str, agent_response: str, metadata: Dict[str, Any] = None) -> None:
        """Add a conversation turn to memory."""
        
        turn = {
            "timestamp": datetime.now().isoformat(),
            "user": user_input,
            "agent": agent_response,
            "metadata": metadata or {}
        }
        
        self.conversations.append(turn)
        self._save()
    
    def update_context(self, key: str, value: Any) -> None:
        """Update context information."""
        
        self.context[key] = value
        self._save()
    
    def get_context(self, key: str) -> Optional[Any]:
        """Retrieve context information."""
        
        return self.context.get(key)
    
    def get_recent_conversations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent conversation turns."""
        
        return self.conversations[-limit:]
    
    def search_conversations(self, query: str) -> List[Dict[str, Any]]:
        """Search conversation history."""
        
        query_lower = query.lower()
        results = []
        
        for conv in self.conversations:
            if query_lower in conv.get("user", "").lower() or query_lower in conv.get("agent", "").lower():
                results.append(conv)
        
        return results
    
    def clear_history(self) -> None:
        """Clear conversation history."""
        
        self.conversations = []
        self._save()
    
    def _save(self) -> None:
        """Save memory to disk."""
        
        try:
            data = {
                "conversations": self.conversations,
                "context": self.context
            }
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save memory: {e}")
    
    def _load(self) -> None:
        """Load memory from disk."""
        
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    self.conversations = data.get("conversations", [])
                    self.context = data.get("context", {})
                    logger.info(f"Loaded {len(self.conversations)} conversation turns")
            except Exception as e:
                logger.warning(f"Failed to load memory: {e}")