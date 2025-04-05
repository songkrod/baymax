import re
from config.settings import settings
from utils.file import ensure_file
import datetime
from utils.logger import logger

# Blacklist phrases - คำหรือวลีที่ Whisper มักจะ hallucinate
BLACKLIST_PHRASES = [
    "บรรยายธรรมอิสลามครูแอ",
    "อ.อิสมาแอล วิสุทธิปราณี",
    "โปรดติดตามตอนต่อไป",
    "บรรยายธรรม",
    "ตอนต่อไป",
    "บทสวด",
    "อิสมาแอล",
    "วิสุทธิปราณี"
]

# สร้างไฟล์ log เปล่า
hallucination_log = ensure_file(settings.HALLUCINATION_LOG_PATH)

def is_blacklisted(text: str) -> bool:
    """ตรวจสอบว่าข้อความมีวลีที่ไม่ต้องการหรือไม่"""
    text = text.strip().lower()
    for phrase in BLACKLIST_PHRASES:
        if phrase.lower() in text:
            return True
    return False

def log_filtered(text: str, reason: str):
    """บันทึกข้อความที่ถูกกรองออก"""
    timestamp = datetime.datetime.now().isoformat()
    with open(hallucination_log, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] ❌ filtered ({reason}): {text}\n")

async def is_valid_transcript(text: str) -> bool:
    """
    ตรวจสอบว่าข้อความที่ได้จาก Whisper เป็น hallucination หรือไม่
    """
    if not text or text.strip() == "":
        return False

    if is_blacklisted(text):
        print(f"ข้อความถูกกรองออกเพราะตรงกับ blacklist: {text}")
        log_filtered(text, "blacklist")
        return False

    return True
