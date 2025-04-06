from skills.core.listen.voice_embedder import extract_embedding
from agent.memory_access.memory_manager import MemoryManager
from agent.reasoning.voice_identity import VoiceIdentifier
from services.asr import transcribe_audio
from utils.logger import logger

memory = MemoryManager()
voice_identifier = VoiceIdentifier()

async def process_audio(audio_bytes: bytes) -> tuple[str, str]:
    """
    ประมวลผลเสียง → ข้อความ และ user_id ที่พูด
    """
    try:
        logger.info("[🔍] เริ่มประมวลผลเสียง...")
        
        # 🔎 ระบุตัวผู้พูด
        user_id = voice_identifier.recognize_speaker(audio_bytes)
        logger.info(f"[🧠] ผู้พูด: {user_id}")

        # 📝 แปลงเสียงเป็นข้อความ
        text = await transcribe_audio(audio_bytes)
        text = text.strip()

        if not text:
            logger.warning("[⚠️] ไม่พบข้อความจากเสียง")
            return "", user_id

        logger.debug(f"[👂] ผู้ใช้ {user_id} พูดว่า: {text}")
        return text, user_id

    except Exception as e:
        logger.error(f"[❌] process_audio error: {e}")
        return "", "unknown"