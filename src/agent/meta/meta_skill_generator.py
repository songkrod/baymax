# src/agent/meta/meta_skill_generator.py

import os
from config.settings import settings
from services.llm import llm
from utils.logger import logger

GENERATED_SKILL_PATH = settings.SKILLS_GENERATED_PATH
os.makedirs(GENERATED_SKILL_PATH, exist_ok=True)

def sanitize_name(name: str) -> str:
    return name.lower().replace(" ", "_").replace("-", "_").strip("._")

def suggest_missing_skill(message: str, context: str = "") -> dict:
    """
    วิเคราะห์ skill ที่ควรมี → คืนเป็น JSON {"skill_name", "description", "example_code"}
    """
    prompt = f"""
    ผู้ใช้ถามว่า:
    "{message}"

    ขณะนี้ระบบมี context เพิ่มเติมดังนี้:
    "{context}"

    แต่ยังไม่สามารถตอบได้ดีพอ
    กรุณาเสนอชื่อสกิลที่ควรเพิ่ม **โดยใช้ชื่อภาษาอังกฤษเท่านั้น** เช่น "weather_lookup" หรือ "location_reasoner"

    อธิบายด้วยว่า skill นี้ช่วยตอบคำถามได้ยังไง
    และให้ตัวอย่างโค้ด Python เบื้องต้นของ skill นั้นแบบง่าย ๆ

    กรุณาตอบกลับในรูปแบบ JSON ที่ประกอบด้วย:
    {{
        "skill_name": ..., 
        "description": ..., 
        "example_code": ...
    }}
    """
    
    response = llm.respond(prompt)
    return llm.safe_json(response)

def generate_skill(user_input: str, user_id: str = "self") -> str:
    """
    วิเคราะห์ skill ที่ควรมี และเขียนไฟล์ skill ลงในระบบ
    คืนชื่อไฟล์ที่สร้าง หรือ "" ถ้าไม่สำเร็จ
    """
    result = suggest_missing_skill(user_input)

    if not result or "skill_name" not in result or "example_code" not in result:
        logger.warning("[🛠️] ไม่สามารถวิเคราะห์ skill ได้จาก input นี้")
        return ""

    name = sanitize_name(result["skill_name"])
    filename = f"{name}.py"
    filepath = os.path.join(GENERATED_SKILL_PATH, filename)

    if os.path.exists(filepath):
        logger.info(f"[📦] skill {filename} มีอยู่แล้ว")
        return filename

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(result["example_code"].strip())

    logger.info(f"[🧠] สร้าง skill ใหม่: {filename}")
    return filename