from services.memory.providers.chroma_memory import ChromaMemory
from services.memory.providers.json_memory import JsonMemory
from services.memory.providers.in_memory import InMemoryMemory
from config.settings import settings

def get_memory_backend():
    backend = settings.MEMORY_BACKEND

    if backend == "chroma":
        return ChromaMemory()
    elif backend == "json":
        return JsonMemory()
    elif backend == "in_memory":
        return InMemoryMemory()
    else:
        raise ValueError(f"Memory backend '{backend}' is not supported yet.")
