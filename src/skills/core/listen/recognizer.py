"""
Voice recognition module for speaker identification using resemblyzer.
"""

from pathlib import Path
import numpy as np
from typing import Optional, Dict, Tuple
import soundfile as sf
import hashlib
from resemblyzer import VoiceEncoder, preprocess_wav
from config.settings import settings
from utils.logger import logger
from skills.core.speech.speaker import say
from agent.brain.gpt_agent import gpt_agent
from agent.memory_access.user_memory import user_memory
from skills.core.listen.listener import record_and_transcribe
from agent.brain.text_analyzer import text_analyzer

class VoiceRecognizer:
    """Class for handling voice recognition using resemblyzer."""
    
    def __init__(self):
        """Initialize voice recognizer."""
        # Create directories
        self.voices_dir = Path(settings.VOICE_SAMPLES_DIR)
        self.embeddings_dir = Path(settings.VOICE_EMBEDDINGS_DIR)
        self.voices_dir.mkdir(parents=True, exist_ok=True)
        self.embeddings_dir.mkdir(parents=True, exist_ok=True)
        
        # Load resemblyzer model
        self.encoder = VoiceEncoder()
        
        # Load existing embeddings
        self.embeddings: Dict[str, np.ndarray] = {}
        self._load_embeddings()
        
    def _load_embeddings(self) -> None:
        """Load all existing voice embeddings."""
        for embedding_file in self.embeddings_dir.glob("*.npy"):
            name = embedding_file.stem
            self.embeddings[name] = np.load(str(embedding_file))
            
    def _compute_embedding(self, wav_path: str) -> np.ndarray:
        """Compute voice embedding from WAV file.
        
        Args:
            wav_path: Path to WAV file
            
        Returns:
            Voice embedding array
        """
        # Load and preprocess WAV
        wav, sr = sf.read(wav_path)
        wav = preprocess_wav(wav)
        
        # Get embedding
        embedding = self.encoder.embed_utterance(wav)
        return embedding
        
    def _save_voice_sample(self, wav_path: str, user_id: str) -> str:
        """Save voice sample WAV file.
        
        Args:
            wav_path: Source WAV file path
            user_id: User identifier
            
        Returns:
            Path to saved sample
        """
        target_path = self.voices_dir / f"{user_id}.wav"
        # Copy the file instead of moving it
        import shutil
        shutil.copy2(wav_path, target_path)
        return str(target_path)
        
    def _save_embedding(self, user_id: str, embedding: np.ndarray) -> None:
        """Save voice embedding.
        
        Args:
            user_id: User identifier
            embedding: Voice embedding array
        """
        path = self.embeddings_dir / f"{user_id}.npy"
        np.save(str(path), embedding)
        self.embeddings[user_id] = embedding
        
    def _generate_user_id(self, wav_path: str) -> str:
        """Generate a safe user ID from voice sample.
        
        Args:
            wav_path: Path to voice sample
            
        Returns:
            Safe user ID string
        """
        # Create hash from file content for consistency
        hash_obj = hashlib.md5()
        with open(wav_path, 'rb') as f:
            hash_obj.update(f.read())
        hash_str = hash_obj.hexdigest()
        return f"user_{hash_str[:8]}"
        
    def find_matching_user(self, wav_path: str, threshold: float = 0.65) -> Tuple[Optional[str], float]:
        """Find user with matching voice.
        
        Args:
            wav_path: Path to WAV file
            threshold: Minimum similarity threshold
            
        Returns:
            Tuple of (matching user ID or None, highest similarity score)
        """
        if not self.embeddings:
            return None, 0.0
            
        # Get embedding for new voice
        new_embedding = self._compute_embedding(wav_path)
        
        # Compare with all known embeddings
        best_match = None
        best_score = 0.0
        
        for user_id, known_embedding in self.embeddings.items():
            # Compute cosine similarity
            score = float(np.inner(new_embedding, known_embedding) / 
                        (np.linalg.norm(new_embedding) * np.linalg.norm(known_embedding)))
            print(f"ตรวจเสียงกับ {user_id}: similarity = {score:.4f}")
            if score > best_score:
                best_score = score
                best_match = user_id
                
        # Return match only if above threshold
        if best_score >= threshold:
            logger.info(f"[🎯] ระบุตัวตนได้: {best_match} (ความมั่นใจ {best_score:.2f})")
            self.update_user_voice(best_match, wav_path)
            return best_match, best_score
            
        return None, best_score
        
    def update_user_voice(self, user_id: str, wav_path: str) -> None:
        """Update or create voice embedding for user.
        
        Args:
            user_id: User identifier
            wav_path: Path to WAV file
        """
        # Save voice sample
        saved_path = self._save_voice_sample(wav_path, user_id)
        
        # Compute and save embedding
        embedding = self._compute_embedding(saved_path)
        self._save_embedding(user_id, embedding)
        
        logger.info(f"[✅] อัพเดทเสียงของ {user_id} เรียบร้อยแล้ว")
        
    async def identify_user(self, wav_path: str, name: Optional[str] = None, should_ask_name: bool = True) -> Tuple[str, bool]:
        """Process voice sample to identify or create user.
        
        Args:
            wav_path: Path to voice sample WAV file
            name: Optional name for new users
            should_ask_name: Whether to ask for name if not recognized
            
        Returns:
            Tuple of (user_id, is_new_user)
        """
        # Try to find matching user
        matching_user_id, _ = self.find_matching_user(wav_path)
        
        if matching_user_id:
            # Found existing user
            # Update their voice profile with new sample
            self.update_user_voice(matching_user_id, wav_path)
            return matching_user_id, False
        else:
            # Create new user
            new_user_id = self._generate_user_id(wav_path)
            
            # Save voice sample and create embedding
            self.update_user_voice(new_user_id, wav_path)
            
            # Create user profile
            user_memory.update_memory("basic_info", {
                "name": name,
                "voice_sample": str(self.voices_dir / f"{new_user_id}.wav")
            }, new_user_id)
            
            return new_user_id, True
            
    async def process_command(self, text: Optional[str] = None) -> str:
        """Process voice command and return response.
        
        Args:
            text: Optional transcribed text (if already available)
            
        Returns:
            Assistant's response
        """
        # Record and transcribe if text not provided
        if text is None:
            text = await record_and_transcribe()
            
        if not text:
            return "ขออภัยครับ ผมไม่ได้ยินเสียงพูดที่ชัดเจน"
            
        try:
            # Use the cached audio file for voice identification
            user_id, is_new_user = await self.identify_user(settings.LAST_AUDIO_CACHE_PATH)
            
            # Set current user in GPT agent
            gpt_agent.set_current_user(user_id)
            
            # Process command with GPT agent first to avoid delay
            response = await gpt_agent.chat(text)
            
            # If new user, ask for name after getting response
            if is_new_user:
                say("ขออภัยครับ ผมยังจำเสียงของคุณไม่ได้")
                say("รบกวนแนะนำตัวหน่อยได้ไหมครับ?")
                name_text = await record_and_transcribe()
                if name_text:
                    # Extract name using GPT
                    name = await text_analyzer.extract_name(name_text)
                    if name:
                        # Update user profile with name
                        user_memory.update_memory("basic_info", {"name": name}, user_id)
                        say(f"ยินดีที่ได้รู้จักครับคุณ{name} ผมจะจำเสียงของคุณไว้นะครับ")
            
            return response
            
        except Exception as e:
            logger.error(f"[❌] เกิดข้อผิดพลาดในการประมวลผลคำสั่ง: {str(e)}")
            return f"ขออภัยครับ มีข้อผิดพลาดเกิดขึ้น: {str(e)}"
            
    async def process_wake_word(self, wav_path: str) -> None:
        """Process voice during wake word detection.
        
        Args:
            wav_path: Path to voice sample WAV file
        """
        try:
            # Always identify and store voice during wake word
            await self.identify_user(wav_path)
        except Exception as e:
            logger.error(f"[❌] เกิดข้อผิดพลาดในการจดจำเสียง: {str(e)}")

# Global instance
voice_recognizer = VoiceRecognizer() 