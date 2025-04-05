import json
from typing import Dict, List
from agent.brain.gpt_agent import gpt_agent
from skills.core.speech.speaker import say
from utils.logger import logger
from agent.memory_access.conversation_memory import get_conversation_history
from skills.core.listen.recognizer import voice_recognizer

async def process_command(text: str) -> None:
    """Process voice command.
    
    Args:
        text: Transcribed text from voice
    """
    # Process command with voice recognizer
    response = await voice_recognizer.process_command(text)
    
    # Speak response
    say(response)
    logger.info(f"[🤖] {response}")

async def analyze_conversation(messages: List[Dict]) -> Dict:
    """
    วิเคราะห์บทสนทนาทั้งหมดเพื่อเข้าใจ intent ที่แท้จริง
    
    Args:
        messages (List[Dict]): ประวัติข้อความในการสนทนา
    
    Returns:
        Dict: ผลการวิเคราะห์ intent
    """
    analysis_prompt = f"""
    วิเคราะห์บทสนทนาต่อไปนี้เพื่อเข้าใจความต้องการที่แท้จริงของผู้ใช้ในบริบทของการสนทนาภาษาไทย:
    
    {get_conversation_history(messages)}
    
    พิจารณาจาก:
    1. ความต่อเนื่องของบทสนทนาในบริบทวัฒนธรรมไทย
    2. การตอบสนองของผู้ใช้ต่อคำตอบที่ได้รับ
    3. คำสำคัญและสำนวนไทยที่เกี่ยวข้อง
    4. ความเชื่อมโยงระหว่างประโยคต่างๆ ในบริบทไทย
    
    ตอบกลับในรูปแบบ JSON โดยใช้คำอธิบายเป็นภาษาไทยทั้งหมด ดังนี้:
    {{
      "type": "คำสั่ง" | "ความรู้" | "ระบบ" | "ไม่แน่ใจ",
      "intent": "ชื่อ intent ที่สื่อความหมายชัดเจนเป็นภาษาอังกฤษเท่านั้น เช่น generate_flirt_sentence, find_recommend_food, turn_on_light, capture_image, connect_to_wifi, etc.",
      "confidence": 0.0 ถึง 1.0,
      "skill_file": "ชื่อไฟล์ .py (ถ้า type เป็น คำสั่ง)",
      "dependencies": ["ชื่อ library (ถ้ามี)"],
      "import_as": ["ชื่อ import"],
      "hardware": ["ชื่อ hardware ที่ต้องใช้"],
      "explanation": "คำอธิบายหรือคำตอบที่สมเหตุสมผล เป็นภาษาไทยที่เข้าใจง่าย",
      "extracted_entities": {{
        "key": "คำสำคัญที่พบในบทสนทนา"
      }}
    }}
    
    หมายเหตุ:
    1. ถ้า confidence น้อยกว่า 0.7 ให้ตอบ type เป็น "ไม่แน่ใจ"
    2. intent ควรสะท้อนความต้องการที่แท้จริง เช่น "ขอคำหวาน" ไม่ใช่แค่ "เข้าใจบทสนทนา"
    3. คำอธิบายต้องเป็นภาษาไทยที่เป็นธรรมชาติและขี้เล่น ไม่จริงจังมาก
    """

    try:
        response = await gpt_agent.chat(get_conversation_history(messages), analysis_prompt)
        result = json.loads(response)
        
        # แปลง type กลับเป็นภาษาอังกฤษตามที่ระบบต้องการ
        type_mapping = {
            "คำสั่ง": "action",
            "ความรู้": "knowledge",
            "ระบบ": "system",
            "ไม่แน่ใจ": "unknown"
        }
        result["type"] = type_mapping.get(result["type"], "unknown")
        
        return result
        
    except json.JSONDecodeError:
        logger.error("[❌] ไม่สามารถแปลง response เป็น JSON ได้")
        return {
            "type": "unknown",
            "intent": "ข้อผิดพลาด",
            "confidence": 0.0,
            "explanation": "ขออภัยครับ เกิดข้อผิดพลาดในการวิเคราะห์บทสนทนา"
        }
    except Exception as e:
        logger.error(f"[❌] เกิดข้อผิดพลาดในการวิเคราะห์บทสนทนา: {e}")
        return {
            "type": "unknown",
            "intent": "ข้อผิดพลาด",
            "confidence": 0.0,
            "explanation": "ขออภัยครับ เกิดข้อผิดพลาดในการวิเคราะห์บทสนทนา"
        }