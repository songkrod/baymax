from config.settings import settings
from utils.file import ensure_file
from typing import Optional
import json

path = ensure_file(settings.SELF_KNOWLEDGE_PATH, [])

def load_self_knowledge():
    """โหลดข้อมูลความจำเกี่ยวกับ self knowledge ที่เคยสร้าง"""
    return json.load(open(path, encoding="utf-8"))

def save_self_knowledge(data):
    """บันทึกข้อมูล self knowledge ลงไฟล์"""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def add_self_knowledge_record(
    intent: str,
    skill_file: str,
    hardware: list = [],
    dependencies: list = [],
    explanation: str = "",
    requested_by: str = None
):
    memory = load_self_knowledge()
    memory.append({
        "intent": intent,
        "skill_file": skill_file,
        "hardware": hardware,
        "dependencies": dependencies,
        "explanation": explanation,
        "requested_by": requested_by,
    })
    save_self_knowledge(memory)