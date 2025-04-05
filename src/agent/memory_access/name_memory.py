from config.settings import settings
from utils.file import ensure_file
import json

path = ensure_file(settings.NAME_MEMORY_PATH, [])

def load_name_memory():
    """โหลดข้อมูลความจำเกี่ยวกับ name memory ที่เคยสร้าง"""
    return json.load(open(path, encoding="utf-8"))

def save_name_memory(data):
    """บันทึกข้อมูล name memory ลงไฟล์"""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def add_name_to_memory(name):
    """เพิ่มชื่อใหม่เข้าไปใน name memory"""
    name_memory = load_name_memory()
    name_memory.append(name.lower())
    save_name_memory(name_memory)