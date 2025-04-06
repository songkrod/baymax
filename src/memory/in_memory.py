
from typing import List
from .base import BaseMemory
from .schema import MemoryItem

class InMemoryMemory(BaseMemory):
    def __init__(self):
        self.memory = {}

    def add_memory(self, item: MemoryItem):
        self.memory.setdefault(item.user_id, []).append(item)

    def get_memories(self, user_id: str, limit: int = 10) -> List[MemoryItem]:
        return self.memory.get(user_id, [])[-limit:]

    def search(self, user_id: str, query: str, top_k: int = 5) -> List[MemoryItem]:
        return self.get_memories(user_id, limit=top_k)
