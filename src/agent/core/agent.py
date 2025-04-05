from config.settings import settings
from skills.core.listen.listener import record_and_transcribe
from skills.core.speech.speaker import say
from utils.logger import logger
from agent.brain.detector import is_wake_word
from skills.core.listen.recognizer import voice_recognizer

async def wait_for_wake_word() -> bool:
    say(f"สวัสดีครับ ผมชื่อ {settings.ROBOT_NAME} เรียกชื่อผมได้เลยถ้าต้องการให้ช่วยนะครับ")
    logger.info(f"[👋] สวัสดีครับ ผมชื่อ {settings.ROBOT_NAME} เรียกชื่อผมได้เลยถ้าต้องการให้ช่วยนะครับ")

    try:
        while True:
            text = await record_and_transcribe()
            if text.strip() == "":
                continue
        
            logger.debug(f"[👂] ได้ยิน: {text}")
        
            # ตรวจสอบว่าในประโยคมีการเรียกชื่อหุ่นไหม
            if await is_wake_word(text):
                logger.info(f"[👋] ได้ยินการเรียกชื่อ: {settings.ROBOT_NAME}")
                # Process voice during wake word
                await voice_recognizer.process_wake_word(settings.LAST_AUDIO_CACHE_PATH)
                return True
    except Exception as e:
        logger.error(f"[❌] เกิดข้อผิดพลาดในการรอรับคำสั่ง: {str(e)}")
        return False

async def wait_for_command():
    say(f"ผมอยู่ตรงนี้ครับ สงสัยอะไรก็ถามได้ครับ")
    print("รอคำสั่ง...")
    logger.info("รอคำสั่ง...")
    while True:
        text = await record_and_transcribe()
        if text.strip() == "":
            continue
        
        logger.debug(f"[👂] ได้ยิน: {text}")
        # Process command through voice recognizer
        response = await voice_recognizer.process_command(text)
        say(response)

async def run():
    print("เริ่มการทำงาน...")
    logger.info("เริ่มการทำงาน...")
    wake = False
    while True:
        if not wake:
            wake = await wait_for_wake_word()
        else:
            await wait_for_command()

