from agent.memory_access.memory_manager import MemoryManager
from services.llm.agent import llm
from uuid import uuid4

memory = MemoryManager()

# เก็บ intent, references, และ conversation log

def track_conversation(user_id: str, message: str, reply: str, emotion: str):
    # สร้าง conversation_id อิงจาก user_id (หรือใช้ uuid หากต้องการ session แยก)
    conversation_id = user_id

    # ตรวจ intent และ reference
    intent = llm.classify_intent(message)
    references = extract_references(reply)  # mock ได้ตอนแรก

    # บันทึกข้อความทั้งสองฝั่ง (ระยะยาว - ไฟล์)
    memory.remember_conversation(conversation_id, user_id, "user", message)
    memory.remember_conversation(conversation_id, user_id, "assistant", reply)

    # ปิด conversation และเก็บข้อมูล intent/references
    memory.end_conversation(conversation_id, intent=intent, refs=references)


def extract_references(text: str):
    # mock แบบง่าย — ในอนาคตสามารถใช้ GPT ช่วยดึง reference ได้
    return []