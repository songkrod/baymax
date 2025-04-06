# src/agent/memory_access/self_knowledge.py

import json
from utils.file import ensure_file
from config.settings import settings
from agent.memory_access.default_self_knowledge import DEFAULT_SELF_KNOWLEDGE

class SelfKnowledge:
    KNOWLEDGE_PATH = settings.SELF_KNOWLEDGE_PATH

    def __init__(self):
        ensure_file(self.KNOWLEDGE_PATH, default=DEFAULT_SELF_KNOWLEDGE)

    def get_knowledge(self):
        with open(self.KNOWLEDGE_PATH, "r") as f:
            return json.load(f)

    def update_knowledge(self, data: dict):
        with open(self.KNOWLEDGE_PATH, "w") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)