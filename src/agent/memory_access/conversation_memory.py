import os
import json
from datetime import datetime
from typing import List
from utils.file import ensure_file
from config.settings import settings

class ConversationMemory:
    CONV_DATA_PATH = settings.CONVERSATION_MEMORY_PATH

    def __init__(self):
        os.makedirs(self.CONV_DATA_PATH, exist_ok=True)

    def log_message(self, conversation_id: str, role: str, content: str):
        path = os.path.join(self.CONV_DATA_PATH, f"{conversation_id}.json")
        ensure_file(path, default={
            "conversation_id": conversation_id,
            "messages": [],
            "timestamp": datetime.utcnow().isoformat()
        })

        with open(path, "r") as f:
            data = json.load(f)

        data["messages"].append({
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        })

        with open(path, "w") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def end_conversation(self, conversation_id: str, final_intent: str, references: List[str]):
        path = os.path.join(self.CONV_DATA_PATH, f"{conversation_id}.json")
        ensure_file(path)
        with open(path, "r") as f:
            data = json.load(f)

        data["final_intent"] = final_intent
        data["references"] = references

        with open(path, "w") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def get_last_conversations(self, user_id: str, limit: int = 5):
        convs = []
        for fname in os.listdir(self.CONV_DATA_PATH):
            if fname.endswith(".json"):
                path = os.path.join(self.CONV_DATA_PATH, fname)
                with open(path, "r") as f:
                    data = json.load(f)
                    if data.get("user_id") == user_id:
                        convs.append(data)
        return sorted(convs, key=lambda x: x["timestamp"], reverse=True)[:limit]
