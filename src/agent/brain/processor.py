# src/agent/brain/processor.py

from agent.memory_access.memory_manager import MemoryManager
from agent.reasoning.voice_identity import VoiceIdentifier
from agent.retrievers.retriever import store_memory, retrieve_context
from services.asr.agent import asr
from services.llm.agent import llm
from utils.logger import logger

memory = MemoryManager()
voice_identifier = VoiceIdentifier()

async def process_audio(audio_bytes: bytes) -> tuple[str, str]:
    """
    ประมวลผลเสียง → ความจำ → ตอบกลับจาก GPT
    คืนค่า: (ข้อความตอบกลับ, user_id)
    """
    try:
        logger.info("[🔍] เริ่มประมวลผลเสียง...")

        # 🔎 ระบุตัวผู้พูด
        user_id = voice_identifier.recognize_speaker(audio_bytes)
        logger.info(f"[🧠] ผู้พูด: {user_id}")

        # 📝 แปลงเสียงเป็นข้อความ
        text = await asr.transcribe(audio_bytes)
        text = text.strip()

        if not text:
            logger.warning("[⚠️] ไม่พบข้อความจากเสียง")
            return "", user_id

        logger.debug(f"[👂] ผู้ใช้ {user_id} พูดว่า: {text}")

        # 💾 เก็บลงความจำ
        store_memory(user_id=user_id, text=text, source="voice")

        # 🧠 ดึง context ที่เกี่ยวข้อง
        context_items = retrieve_context(user_id=user_id, query=text, top_k=3)
        context = "\n".join([item.text for item in context_items])

        # 💬 ใช้ GPT สร้างคำตอบ
        reply = llm.respond(message=text, memory=context)

        logger.info(f"[💡] คำตอบจาก GPT: {reply}")
        return reply, user_id

    except Exception as e:
        logger.error(f"[❌] process_audio error: {e}")
        return "", "unknown"
