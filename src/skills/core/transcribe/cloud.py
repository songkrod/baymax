import os
from openai import OpenAI
from config.settings import settings
from config.instances import openai_client
from utils.logger import logger
import json

CACHE_PATH = settings.WHISPER_CACHE_PATH

def load_cache():
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, "r") as f:
            return json.load(f)
    return {}

def save_cache(cache):
    with open(CACHE_PATH, "w") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

whisper_cache = load_cache()

async def transcribe_cloud(file_path: str) -> str:
    try:
        logger.info("[☁️] ส่งไฟล์เข้า Cloud Whisper (mp3)...")

        file_hash = str(os.path.getmtime(file_path))
        if file_hash in whisper_cache:
            logger.info("[⚡] ใช้คำแปลจาก cache")
            result = whisper_cache[file_hash]
            logger.debug(f"[👂 Whisper Cloud ได้ยินว่า]: {result}")
            return result

        with open(file_path, "rb") as f:
            response = await openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                response_format="text",
                language="th",
                temperature=0
            )

        result = response.strip()
        logger.debug(f"[👂 Whisper Cloud ได้ยินว่า]: {result}")
        whisper_cache[file_hash] = result
        save_cache(whisper_cache)
        return result
    except Exception as e:
        logger.error(f"[❌] ผิดพลาดในการส่งไฟล์เข้า Cloud Whisper: {e}")
        return ""
