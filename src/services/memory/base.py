from abc import ABC, abstractmethod
from typing import List
from datetime import datetime
from memory.schema import MemoryItem

class BaseMemory(ABC):
    @abstractmethod
    def add_memory(self, item: MemoryItem):
        pass

    @abstractmethod
    def get_memories(self, user_id: str, limit: int = 10) -> List[MemoryItem]:
        pass

    @abstractmethod
    def search(self, user_id: str, query: str, top_k: int = 5) -> List[MemoryItem]:
        pass