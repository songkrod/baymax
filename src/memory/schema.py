
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class MemoryItem(BaseModel):
    id: str
    user_id: str
    text: str
    source: str
    timestamp: datetime
    tags: Optional[List[str]] = []
    embedding: Optional[List[float]] = None
