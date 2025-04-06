from typing import List
from services.memory.base import BaseMemory
from memory.schema import MemoryItem

class InMemoryMemory(BaseMemory):
    def __init__(self):
        self.index = []

    def add_memory(self, item: MemoryItem):
        self.index.append(item)

    def get_memories(self, user_id: str, limit: int = 10) -> List[MemoryItem]:
        return [m for m in self.index if m.user_id == user_id][-limit:]

    def search(self, user_id: str, query: str, top_k: int = 5) -> List[MemoryItem]:
        return self.get_memories(user_id, limit=top_k)