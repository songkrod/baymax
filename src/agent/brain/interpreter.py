# 📄 src/agent/brain/interpreter.py

from agent.reasoning.name_reasoner import is_name_called_in_text, extract_uncertain_name, confirm_and_learn_name
from config.settings import settings

# ในอนาคตสามารถใส่ GPT, rules หรือ classifier เพิ่มได้

def interpret(text: str, user_id: str) -> dict:
    """
    วิเคราะห์ intent และ context จากข้อความที่พูด + user_id
    """
    # INTENT: เรียกชื่อหุ่น (ปลุก)
    if is_name_called_in_text(text):
        return {
            "intent": "call_robot",
            "user_id": user_id,
            "confidence": 1.0
        }

    # INTENT: อาจจะเรียกชื่อหุ่น แต่ยังไม่แน่ใจ (ให้ถามผู้ใช้ก่อน)
    possible_name = extract_uncertain_name(text)
    if possible_name:
        return {
            "intent": "maybe_call_robot",
            "user_id": user_id,
            "possible_name": possible_name,
            "confidence": 0.6
        }

    # INTENT: ยังไม่รู้ แต่เก็บเป็นบทสนทนาทั่วไป
    return {
        "intent": "talk_general",
        "user_id": user_id,
        "text": text,
        "confidence": 0.5
    }
