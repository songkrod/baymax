import os
import platform
import tempfile
from config.settings import settings
from utils.logger import logger
from google.cloud import texttospeech
from hardware.speaker import play_sound

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = settings.GOOGLE_APPLICATION_CREDENTIALS

def get_available_thai_voices():
    """รับรายการ voices ภาษาไทยที่มีอยู่จริง"""
    try:
        client = texttospeech.TextToSpeechClient()
        voices = client.list_voices().voices
        return [v for v in voices if "th-TH" in v.language_codes]
    except Exception as e:
        logger.error(f"[❌] Failed to get voices: {e}")
        return []

def list_available_voices():
    """แสดงรายการ voices ทั้งหมดที่มี"""
    try:
        client = texttospeech.TextToSpeechClient()
        voices = client.list_voices()
        logger.info("=== Available Thai Voices ===")
        for voice in voices.voices:
            if "th-TH" in voice.language_codes:
                logger.info(f"Name: {voice.name}")
                logger.info(f"Gender: {voice.ssml_gender}")
                logger.info("---")
    except Exception as e:
        logger.error(f"[❌] Failed to list voices: {e}")

def speak_google(text, lang="th-TH", voice=settings.TTS_VOICE_NAME):
    logger.info("🔊 กำลังพูดด้วย Google TTS")
    try:
        client = texttospeech.TextToSpeechClient()
        thai_voices = get_available_thai_voices()
        
        # กรอง voices ตาม gender ที่ต้องการ (fix เป็น MALE)
        target_gender = texttospeech.SsmlVoiceGender.MALE
        matching_voices = [v for v in thai_voices if v.ssml_gender == target_gender]
        
        # เลือก voice ที่จะใช้
        if not matching_voices:
            voice = settings.TTS_VOICE_NAME
        else:
            voice_names = [v.name for v in matching_voices]
            if voice not in voice_names:
                voice = voice_names[0]

        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice_params = texttospeech.VoiceSelectionParams(
            language_code=lang,
            name=voice,
            ssml_gender=target_gender
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice_params,
            audio_config=audio_config
        )

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as out:
            out.write(response.audio_content)
            out.flush()
            play_sound(out.name)
    except Exception as e:
        logger.error(f"[❌] Failed to synthesize speech: {e}")
        raise

def speak_system(text):
    system = platform.system()
    if system == "Darwin":
        os.system(f'say -v "Kanya" "{text}"')  # หรือ "Lek"
    elif system == "Linux":
        os.system(f'espeak-ng -v th "{text}"')
    else:
        logger.warning("⚠️ ยังไม่รองรับ TTS บนระบบนี้")

def say(text: str):
    logger.debug(f"[🗣️ baymax ตอบ]: {text}")
    print(f"[🗣️ baymax ตอบ]: {text}")

    if settings.USE_SYSTEM_TTS:
        speak_system(text)
    else:
        speak_google(text)