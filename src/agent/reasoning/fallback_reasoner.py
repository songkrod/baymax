# ✅ fallback_reasoner.py

from services.llm.agent import llm
from agent.meta.meta_skill_handler import handle_missing_skill
from utils.logger import logger
from skills.core.speech.speaker import say

def handle_unknown_intent(user_input: str, user_id: str, context: str = ""):
    """
    เมื่อ Baymax ไม่เข้าใจคำสั่ง → ใช้ GPT วิเคราะห์เจตนา + เสนอ skill ใหม่ถ้าเหมาะสม
    """
    say("ขอโทษครับ ผมยังไม่แน่ใจว่าคุณต้องการอะไร")
    logger.warning(f"[❓] ไม่เข้าใจคำสั่ง: {user_input}")

    # ใช้ meta skill reasoning เสนอ skill ใหม่
    handle_missing_skill(user_input=user_input, context=context, user_id=user_id)


def fallback_response(user_input: str, user_id: str, context: str = ""):
    """
    ใช้ fallback dialog เบื้องต้นก่อนสรุปว่าไม่เข้าใจ
    """
    intent = llm.classify_intent(user_input)
    logger.info(f"[🤔] Fallback ตรวจ intent ซ้ำได้ว่า: {intent}")

    if intent in ("clarification", "unknown"):
        handle_unknown_intent(user_input, user_id, context)
    else:
        say("ผมยังไม่แน่ใจครับ ลองอธิบายใหม่อีกนิดได้ไหมครับ")
