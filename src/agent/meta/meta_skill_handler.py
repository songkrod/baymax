# src/agent/meta/meta_skill_handler.py

from agent.meta.meta_skill_generator import generate_skill
from skills.loader import load_skill
from utils.logger import logger

async def handle_missing_skill(user_input: str, user_id: str = "self") -> str:
    """
    ใช้เมื่อ GPT ไม่เข้าใจคำสั่ง → สร้าง skill ใหม่จาก input
    ถ้าสร้างได้ → โหลดเข้า system และแจ้งผู้ใช้
    """
    skill_filename = generate_skill(user_input, user_id)

    if not skill_filename:
        return "ผมยังไม่สามารถสร้างความสามารถนี้ได้ครับ ลองพูดใหม่อีกครั้งได้ไหมครับ"

    # พยายามโหลด skill
    try:
        load_skill(skill_filename)
        return f"ผมได้เรียนรู้วิธีใหม่ในการช่วยคุณแล้วครับ ลองพูดอีกครั้งนะครับ"
    except Exception as e:
        logger.error(f"[❌] โหลด skill ที่ generate แล้วล้มเหลว: {e}")
        return "ผมสร้างความสามารถใหม่ได้ แต่โหลดเข้า system ไม่สำเร็จครับ ขออภัยด้วยครับ"
