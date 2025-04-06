import re
from agent.memory_access.voice_memory import VoiceMemory
from utils.logger import logger

memory = VoiceMemory()

def extract_name_from_text(text: str) -> str | None:
    # ลองจับชื่อจากประโยคทั่วไป เช่น "จำชื่อผมว่า โอม", "เรียกผมว่าเบย์ก็ได้"
    patterns = [
        r"ชื่อ(ผม|ฉัน|หนู)?ว่า\s*([^\s]+)",
        r"เรียก(ผม|ฉัน|หนู)?ว่า\s*([^\s]+)",
        r"จำชื่อ(ผม|ฉัน|หนู)?ว่า\s*([^\s]+)"
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(2)
    return None

def run(user_id: str, text: str) -> str:
    name = extract_name_from_text(text)
    if not name:
        return "ผมไม่แน่ใจว่าคุณอยากให้เรียกชื่อว่าอะไรครับ ช่วยพูดอีกครั้งได้ไหม"

    memory.remember_name(user_id, name)
    logger.info(f"[📛] จดจำชื่อของผู้ใช้ {user_id} เป็น '{name}' เรียบร้อยแล้ว")
    return f"โอเคครับ ต่อไปผมจะเรียกคุณว่า {name}"