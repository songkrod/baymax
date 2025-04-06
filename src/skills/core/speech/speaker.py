import os
import platform
import tempfile
from typing import List
from config.settings import settings
from utils.logger import logger
from google.cloud import texttospeech
from hardware.speaker import play_sound

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = settings.GOOGLE_APPLICATION_CREDENTIALS

def split_long_text(text: str, max_length: int = 200) -> List[str]:
    """Split long text into smaller chunks for TTS.
    
    Args:
        text: Text to split
        max_length: Maximum length per chunk
        
    Returns:
        List of text chunks
    """
    if len(text) <= max_length:
        return [text]
        
    chunks = []
    current = ""
    
    # Split by sentence endings
    sentences = text.replace(". ", ".|").replace("! ", "!|").replace("? ", "?|").split("|")
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        # If current chunk + new sentence is too long, start new chunk
        if len(current) + len(sentence) > max_length:
            if current:
                chunks.append(current.strip())
            current = sentence
        else:
            if current:
                current += " "
            current += sentence
            
    # Add remaining text
    if current:
        chunks.append(current.strip())
        
    return chunks

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

def speak_google(text: str, lang: str = "th-TH", voice: str = settings.TTS_VOICE_NAME):
    """Speak text using Google Cloud TTS.
    
    Args:
        text: Text to speak
        lang: Language code
        voice: Voice name
    """
    logger.info("🔊 กำลังพูดด้วย Google TTS")
    
    try:
        # Split text into chunks if too long
        chunks = split_long_text(text)
        if len(chunks) > 1:
            logger.debug(f"Split text into {len(chunks)} chunks")
            
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

        voice_params = texttospeech.VoiceSelectionParams(
            language_code=lang,
            name=voice,
            ssml_gender=target_gender
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        # Process each chunk
        for chunk in chunks:
            try:
                synthesis_input = texttospeech.SynthesisInput(text=chunk)
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
                logger.error(f"[❌] Failed to speak chunk: {e}")
                continue
                
    except Exception as e:
        logger.error(f"[❌] Failed to synthesize speech: {e}")
        raise

def speak_system(text: str):
    """Speak text using system TTS."""
    system = platform.system()
    if system == "Darwin":
        os.system(f'say -v "Kanya" "{text}"')  # หรือ "Lek"
    elif system == "Linux":
        os.system(f'espeak-ng -v th "{text}"')
    else:
        logger.warning("⚠️ ยังไม่รองรับ TTS บนระบบนี้")

def say(text: str):
    """Main function to speak text.
    
    Args:
        text: Text to speak
    """
    logger.debug(f"[🗣️ baymax ตอบ]: {text}")
    print(f"[🗣️ baymax ตอบ]: {text}")

    if settings.USE_SYSTEM_TTS:
        speak_system(text)
    else:
        speak_google(text)