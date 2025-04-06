import os
from pydantic_settings import BaseSettings
from pathlib import Path
from dotenv import load_dotenv

env_mode = os.getenv("ENV", "dev")
dotenv_path = Path(f".env.{env_mode}")
if dotenv_path.exists():
    load_dotenv(dotenv_path)
else:
    load_dotenv()

class Settings(BaseSettings):
    # Identity
    ROBOT_NAME: str = "baymax"

    # Core Flags
    USE_GPIO: bool = False
    USE_SYSTEM_TTS: bool = False
    USE_CLOUD_WHISPER: bool = False
    DEBUG: bool = False

    # API Keys
    OPENAI_API_KEY: str = ""
    GOOGLE_APPLICATION_CREDENTIALS: str = "secrets/gcloud_key.json"
    
    # OpenAI
    GPT_MODEL: str = "gpt-3.5-turbo"
    
    # Whisper
    WHISPER_MODE: str = "auto"   # auto / cloud / local
    WHISPER_MODEL: str = "tiny"

    # Paths
    AUDIO_INPUT_PATH: str = "data/input.wav"
    LOG_PATH: str = "data/logs.txt"
    MEMORY_DB_PATH: str = "data/memory.json"

    # Memory files
    LAST_AUDIO_CACHE_PATH: str = "data/caches/last_audio_cache.mp3"
    WHISPER_CACHE_PATH: str = "data/caches/whisper_cache.json"
    HALLUCINATION_LOG_PATH: str = "data/logs/hallucination.log"
    NAME_MEMORY_PATH: str = "data/memories/name_memory.json"
    SELF_KNOWLEDGE_PATH: str = "data/memories/self_knowledge.json"
    CONVERSATION_MEMORY_PATH: str = "data/memories/conversation_memory.json"
    USERS_MEMORY_PATH: str = "data/memories/users"
    VOICE_EMBEDDINGS_DIR: str = "data/voices/embeddings"
    VOICE_SAMPLES_DIR: str = "data/voices/samples"
    VECTOR_STORE_PATH: str = "data/vector_store"

    # AI Providers
    LLM_PROVIDER: str = "openai"
    ASR_PROVIDER: str = "whisper"
    TTS_PROVIDER: str = "google"
    MEMORY_BACKEND: str = "chroma"
    
    # TTS
    TTS_VOICE_NAME: str = "th-TH-Chirp3-HD-Charon"
    TTS_SPEAKING_RATE: float = 1.0
    TTS_PITCH: float = 0.0

    # System
    FALLBACK_RESPONSE: str = "ขอโทษครับ ผมยังไม่เข้าใจ"
    FALLBACK_COMMIT: str = "abc1234"

    # Metadata
    PROJECT_NAME: str = "Baymax Mini"
    VERSION: str = "0.1.0"

    # Logging
    LOG_LEVEL: str = "DEBUG"
    LOG_FILE_SIZE_MB: int = 2
    LOG_BACKUP_COUNT: int = 10
    LOG_DIR: str = "data/logs"
    LOG_FILE: str = "log.log"

    class Config:
        env_file = f".env.{env_mode}"
        case_sensitive = False


settings = Settings()