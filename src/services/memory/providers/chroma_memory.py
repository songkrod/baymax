from chromadb import PersistentClient
from datetime import datetime
from services.memory.base import BaseMemory
from memory.schema import MemoryItem
from config.settings import settings

class ChromaMemory(BaseMemory):
    def __init__(self, persist_path=settings.VECTOR_STORE_PATH, collection_name="baymax_memory"):
        self.client = PersistentClient(path=persist_path)
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def add_memory(self, item: MemoryItem):
        item.ensure_embedding()
        self.collection.add(
            documents=[item.text],
            ids=[item.id],
            embeddings=[item.embedding],
            metadatas=[{
                "user_id": item.user_id,
                "source": item.source,
                "timestamp": item.timestamp.isoformat(),
                "tags": ", ".join(item.tags) if item.tags else ""
            }]
        )

    def get_memories(self, user_id: str, limit: int = 10):
        results = self.collection.get()
        items = []
        for doc, meta, id_ in zip(results['documents'], results['metadatas'], results['ids']):
            if meta.get("user_id") == user_id:
                items.append(MemoryItem(
                    id=id_, user_id=meta["user_id"], text=doc,
                    source=meta["source"],
                    timestamp=datetime.fromisoformat(meta["timestamp"]),
                    tags=[t.strip() for t in meta.get("tags", "").split(",")] if meta.get("tags") else []
                ))
        return items[-limit:]

    def search(self, user_id: str, query: str, top_k: int = 5):
        results = self.collection.query(query_texts=[query], n_results=top_k)
        items = []
        for doc, meta, id_ in zip(results['documents'][0], results['metadatas'][0], results['ids'][0]):
            if meta.get("user_id") == user_id:
                items.append(MemoryItem(
                    id=id_, user_id=meta["user_id"], text=doc,
                    source=meta["source"],
                    timestamp=datetime.fromisoformat(meta["timestamp"]),
                    tags=meta.get("tags", [])
                ))
        return items