import json
from datetime import datetime
from typing import Optional, Dict, List
from utils.logger import logger
from config.settings import settings
from utils.file import ensure_file

path = ensure_file(settings.CONVERSATION_MEMORY_PATH, [])

def load_conversations():
    """โหลดข้อมูลประวัติการสนทนาทั้งหมด"""
    try:
        return json.load(open(path, encoding="utf-8"))
    except Exception as e:
        logger.error(f"[❌] เกิดข้อผิดพลาดในการโหลดบทสนทนา: {e}")
        return []

def save_conversations(data):
    """บันทึกข้อมูลประวัติการสนทนาลงไฟล์"""
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"[❌] เกิดข้อผิดพลาดในการบันทึกบทสนทนา: {e}")

def add_conversation(messages: List[Dict], final_intent: Optional[Dict] = None):
    """
    เพิ่มบทสนทนาใหม่ลงในประวัติ
    
    Args:
        messages (List[Dict]): รายการข้อความในบทสนทนา
        final_intent (Optional[Dict]): intent สุดท้ายที่วิเคราะห์ได้
    """
    conversation_data = {
        "start_time": messages[0]["timestamp"] if messages else datetime.now().isoformat(),
        "end_time": datetime.now().isoformat(),
        "messages": messages,
        "final_intent": final_intent
    }
    
    conversations = load_conversations()
    conversations.append(conversation_data)
    save_conversations(conversations)
    logger.info(f"[💾] บันทึกบทสนทนาเรียบร้อย")

def get_conversation_history(messages: List[Dict]) -> str:
    """
    แปลงรายการข้อความเป็นข้อความต่อเนื่อง
    
    Args:
        messages (List[Dict]): รายการข้อความในบทสนทนา
    
    Returns:
        str: ประวัติการสนทนาในรูปแบบข้อความ
    """
    return "\n".join([
        f"{msg['role']}: {msg['content']}" 
        for msg in messages
    ])

def list_conversations() -> List[Dict]:
    """
    แสดงรายการบทสนทนาทั้งหมดที่บันทึกไว้
    
    Returns:
        List[Dict]: รายการบทสนทนาพร้อมข้อมูลสรุป
    """
    conversations = load_conversations()
    return [{
        "start_time": conv["start_time"],
        "end_time": conv["end_time"],
        "message_count": len(conv["messages"]),
        "final_intent": conv.get("final_intent", {}).get("intent")
    } for conv in conversations] 