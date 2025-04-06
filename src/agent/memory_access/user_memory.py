import os
import json
from utils.file import ensure_file
from config.settings import settings

class UserMemoryManager:    
    USER_DATA_PATH = settings.USERS_MEMORY_PATH

    def __init__(self):
        os.makedirs(self.USER_DATA_PATH, exist_ok=True)

    def get_user_profile(self, user_id: str) -> dict:
        path = os.path.join(self.USER_DATA_PATH, f"{user_id}.json")
        ensure_file(path, default={})
        with open(path, "r") as f:
            return json.load(f)

    def update_user_profile(self, user_id: str, data: dict):
        path = os.path.join(self.USER_DATA_PATH, f"{user_id}.json")
        with open(path, "w") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def add_preference(self, user_id: str, item: str, like: bool = True):
        profile = self.get_user_profile(user_id)
        key = "likes" if like else "dislikes"
        profile.setdefault("preferences", {"likes": [], "dislikes": []})
        if item not in profile["preferences"][key]:
            profile["preferences"][key].append(item)
        self.update_user_profile(user_id, profile)
