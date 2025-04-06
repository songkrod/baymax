import os
import json
import numpy as np
from utils.file import ensure_file
from config.settings import settings
from utils.logger import logger

class VoiceMemory:
    EMBEDDING_PATH = settings.VOICE_EMBEDDINGS_DIR
    SAMPLE_PATH = settings.VOICE_SAMPLES_DIR
    USER_DATA_PATH = settings.USERS_MEMORY_PATH

    def __init__(self):
        os.makedirs(self.SAMPLE_PATH, exist_ok=True)
        os.makedirs(self.EMBEDDING_PATH, exist_ok=True)
        os.makedirs(self.USER_DATA_PATH, exist_ok=True)

    def get_voice_samples(self, user_id: str):
        return [f for f in os.listdir(self.SAMPLE_PATH) if f.startswith(user_id)]

    def save_voice_sample(self, user_id: str, audio_bytes: bytes) -> str:
        # สร้าง folder แยกตาม user
        user_sample_dir = os.path.join(self.SAMPLE_PATH, user_id)
        os.makedirs(user_sample_dir, exist_ok=True)

        # ตั้งชื่อไฟล์แบบ auto increment
        existing = sorted([
            int(f.replace(".wav", "")) for f in os.listdir(user_sample_dir) if f.endswith(".wav")
        ])
        index = (existing[-1] + 1) if existing else 1
        filename = f"{index}.wav"
        path = os.path.join(user_sample_dir, filename)

        with open(path, "wb") as f:
            f.write(audio_bytes)
        return path

    def save_embedding(self, user_id: str, embedding: list[float]):
        path = os.path.join(self.EMBEDDING_PATH, f"{user_id}.npy")
        np.save(path, np.array(embedding))

    def load_embedding(self, user_id: str):
        path = os.path.join(self.EMBEDDING_PATH, f"{user_id}.npy")
        if os.path.exists(path):
            return np.load(path).tolist()
        return None

    def save_user_profile(self, user_id: str, data: dict):
        """
        ใช้ตอนสร้าง user ใหม่ เพื่อบันทึกข้อมูลเริ่มต้น เช่น timestamp และ path ของ sample
        """
        path = os.path.join(self.USER_DATA_PATH, f"{user_id}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def update_user_voice_profile(self, user_id: str, new_sample_path: str):
        """
        ใช้ในกรณีที่ผู้ใช้พูดใหม่ และต้องการเพิ่มตัวอย่างเสียงเข้าไปใน profile เดิม
        """
        profile_path = os.path.join(self.USER_DATA_PATH, f"{user_id}.json")
        ensure_file(profile_path, default={})
        with open(profile_path, "r", encoding="utf-8") as f:
            profile = json.load(f)

        profile.setdefault("voice_samples", [])
        profile["voice_samples"].append(new_sample_path)

        with open(profile_path, "w", encoding="utf-8") as f:
            json.dump(profile, f, ensure_ascii=False, indent=2)

    def list_user_ids(self) -> list[str]:
        return [
            fname.replace(".npy", "")
            for fname in os.listdir(self.EMBEDDING_PATH)
            if fname.endswith(".npy")
        ]

    def get_all_sample_paths(self, user_id: str) -> list[str]:
        user_sample_dir = os.path.join(self.SAMPLE_PATH, user_id)
        if not os.path.exists(user_sample_dir):
            return []
        return [
            os.path.join(user_sample_dir, f)
            for f in os.listdir(user_sample_dir)
            if f.endswith(".wav")
        ]

    def count_samples(self, user_id: str) -> int:
        return len(self.get_all_sample_paths(user_id))

    def set_user_registered(self, user_id: str):
        path = os.path.join(self.USER_DATA_PATH, f"{user_id}.json")
        if not os.path.exists(path):
            return
        with open(path, "r", encoding="utf-8") as f:
            profile = json.load(f)
        profile["pending"] = False
        logger.info(f"[📛] ตั้งค่า user {user_id} เป็น registered")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(profile, f, ensure_ascii=False, indent=2)

    def remember_name(self, user_id: str, name: str):
        path = os.path.join(self.USER_DATA_PATH, f"{user_id}.json")
        ensure_file(path, default={})
        with open(path, "r", encoding="utf-8") as f:
            profile = json.load(f)
        profile["name"] = name
        with open(path, "w", encoding="utf-8") as f:
            json.dump(profile, f, ensure_ascii=False, indent=2)