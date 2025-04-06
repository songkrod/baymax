from agent.reasoning.name_reasoner import is_name_similar_to_robot, confirm_and_learn_name
from agent.memory_access.memory_manager import MemoryManager

memory = MemoryManager()

async def detect_and_learn_name(text: str, user_id: str) -> bool:
    """
    ตรวจสอบว่ามีคำใกล้เคียงกับชื่อหุ่นไหม และถามยืนยันเพื่อบันทึก
    สามารถใช้ได้ทั้งตอนหลับหรือตื่น เพื่อให้เรียนรู้ชื่อใหม่ตลอดเวลา
    """
    possible_name = is_name_similar_to_robot(text)
    if not possible_name:
        return False

    already_known = memory.robot_name.is_known(possible_name)
    if already_known:
        return False

    confirmed = await confirm_and_learn_name(possible_name, user_id)
    return confirmed