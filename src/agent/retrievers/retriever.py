from datetime import datetime
from services.memory.client import get_memory_backend
from memory.schema import MemoryItem

memory = get_memory_backend()

def store_memory(user_id: str, text: str, source: str = "system", tags=None):
    item = MemoryItem(
        id=str(abs(hash(user_id + text)) % (10 ** 12)),
        user_id=user_id,
        text=text,
        source=source,
        timestamp=datetime.now(),
        tags=tags or [],
    )
    memory.add_memory(item)

def retrieve_context(user_id: str, query: str, top_k: int = 3):
    return memory.search(user_id=user_id, query=query, top_k=top_k)