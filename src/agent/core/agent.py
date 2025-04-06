from config.settings import settings
from skills.core.listen.listener import record_audio_raw
from skills.core.speech.speaker import say
from utils.logger import logger

from agent.brain.processor import process_audio
from agent.brain.interpreter import interpret
from agent.reasoning.name_learning import detect_and_learn_name
from agent.memory_access.memory_manager import MemoryManager

memory = MemoryManager()


async def wait_for_wake_word():
    say(f"สวัสดีครับ ผมชื่อ {settings.ROBOT_NAME} เรียกชื่อผมได้เลยถ้าต้องการให้ช่วยนะครับ")
    logger.info("[👋] ฟังคำทักทาย...")

    try:
        while True:
            audio = await record_audio_raw()
            if not audio:
                continue

            text, user_id = await process_audio(audio)
            if not text:
                continue

            result = interpret(text, user_id)

            # ตรวจ intent
            if result["intent"] in ("call_robot", "maybe_call_robot"):
                await detect_and_learn_name(text, user_id)

                profile = memory.user.get_user_profile(user_id) or {}
                name = profile.get("basic_info", {}).get("name", "เพื่อน")
                say(f"สวัสดีครับคุณ{name} ผมพร้อมช่วยแล้วครับ")
                return True

    except Exception as e:
        logger.error(f"[❌] เกิดข้อผิดพลาดในการรอปลุก: {str(e)}")
        return False


async def wait_for_command():
    say(f"ผมอยู่ตรงนี้ครับ สงสัยอะไรก็ถามได้ครับ")
    logger.info("🤖 หุ่นตื่นแล้ว กำลังรอคำสั่ง")

    while True:
        audio = await record_audio_raw()
        if not audio:
            continue

        text, user_id = await process_audio(audio)
        if not text:
            continue

        # วิเคราะห์ intent และเรียนรู้ชื่อเพิ่มเติมได้
        result = interpret(text, user_id)
        await detect_and_learn_name(text, user_id)

        reply = f"คุณพูดว่า '{text}' ใช่ไหมครับ?"  # ยังเป็น placeholder
        say(reply)


async def run():
    logger.info("🤖 กำลังเริ่มการทำงาน...")
    wake = False

    while True:
        if not wake:
            wake = await wait_for_wake_word()
        else:
            await wait_for_command()