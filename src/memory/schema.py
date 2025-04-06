# src/memory/schema.py

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from services.memory.embedding import get_embedding

class MemoryItem(BaseModel):
    id: str
    user_id: str
    text: str
    source: str = "system"
    timestamp: datetime = Field(default_factory=datetime.now)
    tags: Optional[List[str]] = []
    embedding: Optional[List[float]] = None

    def ensure_embedding(self):
        """ฝังเวกเตอร์ให้ตัวเองถ้ายังไม่มี"""
        if self.embedding is None:
            self.embedding = get_embedding(self.text)

    def to_dict(self, exclude_embedding=False):
        """ใช้แทน .dict() ใน Pydantic v2"""
        return self.model_dump(exclude={"embedding"} if exclude_embedding else {})
