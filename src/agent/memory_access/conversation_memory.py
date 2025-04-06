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

def add_conversation(messages: List[Dict], user_id: str, final_intent: Optional[Dict] = None):
    """
    เพิ่มบทสนทนาใหม่ลงในประวัติ
    
    Args:
        messages (List[Dict]): รายการข้อความในบทสนทนา
        user_id (str): รหัสผู้ใช้
        final_intent (Optional[Dict]): intent สุดท้ายที่วิเคราะห์ได้
    """
    if not messages or not isinstance(messages, list):
        logger.warning("[⚠️] ไม่สามารถบันทึกบทสนทนาได้: ข้อมูล messages ไม่ถูกต้อง")
        return
        
    conversation_data = {
        "user_id": user_id,
        "start_time": messages[0].get("timestamp", datetime.now().isoformat()) if messages else datetime.now().isoformat(),
        "end_time": datetime.now().isoformat(),
        "messages": messages,
        "final_intent": final_intent if isinstance(final_intent, dict) else None
    }
    
    try:
        conversations = load_conversations()
        if not isinstance(conversations, list):
            conversations = []
        conversations.append(conversation_data)
        save_conversations(conversations)
        logger.info(f"[💾] บันทึกบทสนทนาเรียบร้อย")
    except Exception as e:
        logger.error(f"[❌] เกิดข้อผิดพลาดในการบันทึกบทสนทนา: {e}")

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

def list_conversations(user_id: Optional[str] = None) -> List[Dict]:
    """
    แสดงรายการบทสนทนาทั้งหมดที่บันทึกไว้
    
    Args:
        user_id (Optional[str]): ถ้าระบุจะแสดงเฉพาะบทสนทนาของผู้ใช้คนนั้น
    
    Returns:
        List[Dict]: รายการบทสนทนาพร้อมข้อมูลสรุป
    """
    conversations = load_conversations()
    if user_id:
        conversations = [conv for conv in conversations if conv.get("user_id") == user_id]
        
    return [{
        "user_id": conv.get("user_id"),
        "start_time": conv["start_time"],
        "end_time": conv["end_time"],
        "message_count": len(conv["messages"]),
        "final_intent": conv.get("final_intent", {}).get("intent")
    } for conv in conversations] 