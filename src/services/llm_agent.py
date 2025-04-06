# src/services/llm_agent.py

from services.llm import complete

# ✨ บุคลิกหลักของ Baymax 2
BASE_PERSONALITY_PROMPT = """
You are Baymax 2, a friendly Thai-speaking soft robot.
You always respond in polite and natural Thai.
You try to understand the user's feelings and intent through conversation.
"""

def build_prompt(user_message: str, memory: str = "", emotion: str = "") -> str:
    """
    ประกอบ prompt สำหรับส่งเข้า LLM โดยรวมบุคลิก + ความจำ + อารมณ์ + ข้อความจากผู้ใช้
    """
    prompt = BASE_PERSONALITY_PROMPT.strip()

    if memory:
        prompt += f"\n\n[Memory]\n{memory.strip()}"

    if emotion:
        prompt += f"\n\n[User emotion is: {emotion.strip()}]"

    prompt += f"\n\n[User says]\n{user_message.strip()}"
    return prompt

def respond(user_message: str, memory: str = "", emotion: str = "") -> str:
    """
    ส่งข้อความพร้อม context ไปยัง LLM แล้วคืนคำตอบกลับ
    """
    prompt = build_prompt(user_message, memory=memory, emotion=emotion)
    return complete(prompt)