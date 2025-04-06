import os
import time
import uuid
import numpy as np
from typing import Optional
from scipy.spatial.distance import cosine
from resemblyzer import VoiceEncoder, preprocess_wav
from agent.memory_access.voice_memory import VoiceMemory

class VoiceIdentifier:
    def __init__(self, threshold=0.75, min_samples_to_register=3):
        self.memory = VoiceMemory()
        self.threshold = threshold
        self.min_samples = min_samples_to_register
        self.encoder = VoiceEncoder()

    def extract_embedding_from_file(self, file_path: str) -> np.ndarray:
        wav = preprocess_wav(file_path)
        return self.encoder.embed_utterance(wav)

    def extract_embedding_from_bytes(self, audio_bytes: bytes) -> np.ndarray:
        from tempfile import NamedTemporaryFile
        with NamedTemporaryFile(suffix=".wav", delete=True) as f:
            f.write(audio_bytes)
            f.flush()
            return self.extract_embedding_from_file(f.name)

    def identify_user(self, embedding: np.ndarray) -> Optional[str]:
        best_match, best_score = None, 1.0
        for user_id in self.memory.list_user_ids():
            saved_emb = self.memory.load_embedding(user_id)
            if saved_emb is None:
                continue
            score = cosine(np.asarray(saved_emb).flatten(), np.asarray(embedding).flatten())
            if score < best_score:
                best_score = score
                best_match = user_id
        if best_score < (1 - self.threshold):
            return best_match
        return None

    def get_average_embedding(self, user_id: str) -> Optional[np.ndarray]:
        sample_paths = self.memory.get_all_sample_paths(user_id)
        if not sample_paths:
            return None
        embeddings = []
        for path in sample_paths:
            try:
                emb = self.extract_embedding_from_file(path)
                embeddings.append(emb)
            except Exception:
                continue
        if not embeddings:
            return None
        return np.mean(embeddings, axis=0)

    def register_new_user(self, audio_bytes: bytes) -> str:
        user_id = f"user_{uuid.uuid4().hex[:6]}"
        sample_path = self.memory.save_voice_sample(user_id, audio_bytes)
        self.memory.save_user_profile(user_id, {
            "created_at": time.time(),
            "voice_samples": [sample_path],
            "pending": True
        })

        # สร้าง embedding เริ่มต้น
        embedding = self.extract_embedding_from_bytes(audio_bytes)
        self.memory.save_embedding(user_id, embedding.tolist())
        return user_id

    def update_user(self, user_id: str, audio_bytes: bytes):
        # บันทึกตัวอย่างเสียงใหม่
        sample_path = self.memory.save_voice_sample(user_id, audio_bytes)
        self.memory.update_user_voice_profile(user_id, sample_path)

        # คำนวณ average embedding ใหม่
        avg_emb = self.get_average_embedding(user_id)
        if avg_emb is not None:
            self.memory.save_embedding(user_id, avg_emb.tolist())

        # Promote user หาก sample >= min_samples
        if self.memory.count_samples(user_id) >= self.min_samples:
            self.memory.set_user_registered(user_id)

    def recognize_speaker(self, audio_bytes: bytes) -> str:
        embedding = self.extract_embedding_from_bytes(audio_bytes)
        user_id = self.identify_user(embedding)
        if user_id:
            self.update_user(user_id, audio_bytes)
        else:
            user_id = self.register_new_user(audio_bytes)
        return user_id