# src/agent/meta/hardware_meta_skill_generator.py

import json
from services.llm import llm
from agent.memory_access.self_knowledge import SelfKnowledge


def generate_hardware_skill(user_input: str, user_id: str = "self") -> dict:
    """
    ใช้ self_knowledge.json เพื่อ generate skill ที่เข้าถึง hardware จริง
    คืนเป็น dict { skill_name, description, example_code }
    """
    # โหลด knowledge ที่ละเอียดมาก
    self_knowledge = SelfKnowledge().get_knowledge()
    hw_summary = json.dumps(self_knowledge["hardware"], indent=2, ensure_ascii=False)

    prompt = f"""
    ผู้ใช้พูดว่า:
    "{user_input}"

    ต่อไปนี้คือความรู้เกี่ยวกับ hardware ทั้งหมดของหุ่น:
    {hw_summary}

    กรุณาสร้าง skill ใหม่ที่สามารถเข้าถึง hardware จริงได้ เช่น:
    - อ่านค่า sensor
    - ควบคุมปั๊ม วาล์ว หรือแสดงผลผ่าน OLED

    ระบุชื่อ skill เป็นภาษาอังกฤษเท่านั้น เช่น "adjust_pressure" หรือ "display_battery_on_eye"
    และแสดงตัวอย่างโค้ด Python เบื้องต้นที่เข้าถึง hardware จริงผ่าน GPIO หรือ library ที่เหมาะสม

    ตอบกลับในรูปแบบ JSON เท่านั้น:
    {{
      "skill_name": ..., 
      "description": ..., 
      "example_code": ...
    }}
    """

    response = llm.respond(prompt)
    return llm.safe_json(response)
