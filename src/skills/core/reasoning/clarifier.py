from services.llm.agent import llm


def clarify_if_uncertain(user_input: str, user_id: str) -> str:
    """
    Use GPT to detect uncertainty and suggest follow-up questions.
    """
    prompt = f"""
    คุณคือหุ่นยนต์ช่วยเหลือที่ฉลาดมาก หากข้อความต่อไปนี้ยังไม่ชัดเจนพอที่จะตอบได้
    ให้คุณแนะนำคำถามกลับเพื่อขอข้อมูลเพิ่มแบบเป็นธรรมชาติ เช่น "หมายถึงที่ไหนครับ?" หรือ "คุณต้องการผมช่วยหาข้อมูลให้ไหม?"

    คำพูดของผู้ใช้: "{user_input}"
    ถ้าเข้าใจแล้วให้ตอบว่า "เข้าใจครับ" แต่ถ้ายังไม่พอให้ถามกลับทันที
    """
    reply = llm.respond(prompt, user_id=user_id)
    return reply.strip()
