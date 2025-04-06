import json
from pathlib import Path
from datetime import datetime
from services.memory.base import BaseMemory
from memory.schema import MemoryItem

class JsonMemory(BaseMemory):
    def __init__(self, path="data/json_memory.json"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.touch(exist_ok=True)
        self._load()

    def _load(self):
        try:
            with self.path.open("r", encoding="utf-8") as f:
                self.data = json.load(f)
        except json.JSONDecodeError:
            self.data = []

    def _save(self):
        with self.path.open("w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def add_memory(self, item: MemoryItem):
        self.data.append(item.dict())
        self._save()

    def get_memories(self, user_id: str, limit: int = 10):
        matches = [MemoryItem(**m) for m in self.data if m["user_id"] == user_id]
        return matches[-limit:]

    def search(self, user_id: str, query: str, top_k: int = 5):
        return self.get_memories(user_id, limit=top_k)