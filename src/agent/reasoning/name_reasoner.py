
from rapidfuzz import fuzz
from agent.memory_access.memory_manager import MemoryManager
from skills.core.speech.speaker import say
from typing import Optional

memory = MemoryManager()

FUZZY_THRESHOLD = 80  # ความคล้ายของชื่อที่ถือว่าใช้ได้

def is_name_called_in_text(text: str) -> bool:
    """
    ตรวจสอบว่ามีการเรียกชื่อหุ่นในข้อความหรือไม่ โดยใช้ fuzzy matching
    """
    name_list = memory.name.get_all_names()
    return any(fuzz.partial_ratio(name.lower(), text.lower()) >= FUZZY_THRESHOLD for name in name_list)

def extract_uncertain_name(text: str) -> Optional[str]:
    """
    หากไม่มีชื่อที่แน่นอน ตรวจสอบว่ามีคำใดในข้อความที่อาจจะเป็นชื่อหุ่นหรือไม่
    เช่น "เบย์แมกซ์", "เบแม", "เพื่อแม็ก" เป็นต้น
    """
    words = text.lower().split()
    known_names = memory.name.get_all_names()
    robot_name = memory.self_knowledge.get_knowledge()["name"].lower()

    for word in words:
        # ต้องไม่ตรงกับชื่อที่จำได้แล้ว
        if all(fuzz.partial_ratio(word, known.lower()) < FUZZY_THRESHOLD for known in known_names):
            # และมีความคล้ายกับชื่อหุ่นมากพอ (อาจจะพูดเพี้ยน)
            if fuzz.partial_ratio(word, robot_name) > 60:
                return word
    return None

async def confirm_and_learn_name(possible_name: str, user_id: str) -> bool:
    """
    ถามผู้ใช้เพื่อยืนยันว่า คำที่น่าสงสัยหมายถึง Baymax หรือไม่
    ถ้าใช่ จะเพิ่มลงใน name_memory
    """
    say(f"ผมได้ยินคำว่า {possible_name} คำนี้หมายถึง Baymax ใช่ไหมครับ?")
    print(f"[❓] ขอคำยืนยัน: '{possible_name}' หมายถึง Baymax ไหม? (พิมพ์ yes/no)")

    answer = input("> ").strip().lower()
    if answer in ["yes", "ใช่", "y", "ได้", "ok", "โอเค"]:
        memory.name.add_name(possible_name)
        return True
    return False

def is_name_similar_to_robot(text: str) -> Optional[str]:
    """
    ฟังก์ชัน wrapper ที่ใช้ logic ของ extract_uncertain_name()
    เพื่อสื่อความหมายว่ากำลังตรวจชื่อที่คล้ายชื่อหุ่น
    """
    return extract_uncertain_name(text)
