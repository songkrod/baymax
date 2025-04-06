# src/agent/meta/hardware_meta_skill_handler.py

import os
from services.llm import llm
from agent.meta.hardware_meta_skill_generator import generate_hardware_skill
from skills.loader import load_skill
from utils.logger import logger
from config.settings import settings


def is_hardware_related(text: str) -> bool:
    """
    ใช้ GPT วิเคราะห์ว่าเป็นคำสั่งที่เกี่ยวกับ hardware หรือไม่ เช่น pump, sensor, oled
    """
    prompt = f"""
    ข้อความต่อไปนี้เป็นคำสั่งหรือคำถามของผู้ใช้:
    "{text}"

    กรุณาตอบว่าเกี่ยวข้องกับการเข้าถึงฮาร์ดแวร์ของหุ่นหรือไม่ เช่น การอ่าน sensor หรือควบคุมปั๊ม วาล์ว OLED ฯลฯ
    ถ้าเกี่ยวข้องให้ตอบว่า: yes
    ถ้าไม่เกี่ยวข้องให้ตอบว่า: no
    """
    result = llm.respond(prompt).strip().lower()
    return "yes" in result


def handle_hardware_skill(user_input: str, user_id: str = "self") -> str:
    if settings.USE_GPIO is False:
        logger.info("[🔌] โหมด GPIO ถูกปิดอยู่ — ข้ามการสร้าง hardware skill")
        return "ตอนนี้ยังไม่ได้เปิดโหมดเชื่อมต่อกับฮาร์ดแวร์ครับ"

    if not is_hardware_related(user_input):
        return "คำสั่งนี้ไม่ได้เกี่ยวกับฮาร์ดแวร์ครับ"

    try:
        result = generate_hardware_skill(user_input, user_id)
        filename = result["skill_name"] + ".py"
        filepath = os.path.join("src/skills/generated", filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(result["example_code"])

        load_skill(filename)
        logger.info(f"[🤖] เพิ่ม hardware skill สำเร็จ: {filename}")
        return f"ผมเรียนรู้วิธีเข้าถึงฮาร์ดแวร์ใหม่เรียบร้อยแล้วครับ: {result['skill_name']}"

    except Exception as e:
        logger.error(f"[❌] สร้าง hardware skill ล้มเหลว: {e}")
        return "ผมยังสร้าง skill นี้ไม่ได้ครับ อาจมีบางอย่างผิดพลาด 🧯"
