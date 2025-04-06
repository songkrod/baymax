
import os
import json
from uuid import uuid4
from typing import List
from datetime import datetime
from .base import BaseMemory
from .schema import MemoryItem

MEMORY_PATH = "data/memories/json"

class JSONMemory(BaseMemory):
    def __init__(self):
        os.makedirs(MEMORY_PATH, exist_ok=True)

    def _get_user_path(self, user_id: str):
        return os.path.join(MEMORY_PATH, f"{user_id}.json")

    def add_memory(self, item: MemoryItem):
        path = self._get_user_path(item.user_id)
        if os.path.exists(path):
            with open(path, 'r') as f:
                data = json.load(f)
        else:
            data = []

        data.append(item.dict())
        with open(path, 'w') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def get_memories(self, user_id: str, limit: int = 10) -> List[MemoryItem]:
        path = self._get_user_path(user_id)
        if not os.path.exists(path):
            return []

        with open(path, 'r') as f:
            data = json.load(f)

        return [MemoryItem(**d) for d in data[-limit:]]

    def search(self, user_id: str, query: str, top_k: int = 5) -> List[MemoryItem]:
        # TODO: Add embedding-based search
        return self.get_memories(user_id, limit=top_k)
