
import json
from utils.file import ensure_file
from config.settings import settings

class NameMemory:
    NAME_MEMORY_PATH = settings.NAME_MEMORY_PATH
    
    def __init__(self):
        ensure_file(self.NAME_MEMORY_PATH, default=[])

    def add_name(self, name: str):
        with open(self.NAME_MEMORY_PATH, "r") as f:
            names = json.load(f)
        if name not in names:
            names.append(name)
        with open(self.NAME_MEMORY_PATH, "w") as f:
            json.dump(names, f, ensure_ascii=False, indent=2)

    def get_names(self) -> list[str]:
        with open(self.NAME_MEMORY_PATH, "r") as f:
            return json.load(f)

    def get_all_names(self) -> list[str]:
        return self.get_names()
