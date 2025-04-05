import os
import webrtcvad
import sounddevice as sd
import asyncio
import tempfile
import numpy as np
from pydub import AudioSegment
from utils.logger import logger
from config.settings import settings
from skills.core.transcribe.cloud import transcribe_cloud
from skills.core.transcribe.local import transcribe_local
from skills.core.speech.speaker import say
from utils.hallucination import is_valid_transcript

VAD_MODE = 3
SAMPLE_RATE = 16000
FRAME_DURATION_MS = 30
FRAME_SIZE = int(SAMPLE_RATE * FRAME_DURATION_MS / 1000)
VAD_SILENCE_DURATION_MS = 300
MIN_SPEECH_DURATION_MS = 500

vad = webrtcvad.Vad(VAD_MODE)

async def record_and_transcribe():
    print("กำลังฟัง...")
    audio_buffer = []
    silence_ms = 0
    total_speech_ms = 0
    triggered = False
    recording_done = asyncio.Event()

    def callback(indata, frames, time, status):
        nonlocal triggered, silence_ms, audio_buffer, total_speech_ms
        if status:
            logger.warning(f"[⚠️] Stream status: {status}")
        pcm_data = indata[:, 0].tobytes()
        is_speech = vad.is_speech(pcm_data, SAMPLE_RATE)
        audio_buffer.append(pcm_data)

        if is_speech:
            if not triggered:
                logger.info("[🎤] ได้ยินเสียงแล้ว บันทึก...")
                triggered = True
            silence_ms = 0
            total_speech_ms += FRAME_DURATION_MS
        elif triggered:
            silence_ms += FRAME_DURATION_MS
            if total_speech_ms > MIN_SPEECH_DURATION_MS and silence_ms > VAD_SILENCE_DURATION_MS:
                recording_done.set()

    stream = sd.InputStream(
        channels=1,
        samplerate=SAMPLE_RATE,
        dtype="int16",
        blocksize=FRAME_SIZE,
        callback=callback
    )

    with stream:
        try:
            await asyncio.wait_for(recording_done.wait(), timeout=7.0)
            logger.info("[⏹️] เสียงเงียบแล้ว ตัดคำทันที")
        except asyncio.TimeoutError:
            logger.info("[⏹️] หมดเวลาบันทึก")
        except Exception as e:
            logger.error(f"[❌] Recording error: {e}")

    if not audio_buffer:
        logger.warning("[⚠️] ไม่พบเสียงพูด")
        return ""

    audio = b"".join(audio_buffer)
    audio_array = np.frombuffer(audio, dtype=np.int16)

    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        segment = AudioSegment(
            audio_array.tobytes(),
            frame_rate=SAMPLE_RATE,
            sample_width=2,
            channels=1
        )
        segment.export(f.name, format="mp3")
        fpath = f.name

    with open(settings.LAST_AUDIO_CACHE_PATH, "wb") as out:
        out.write(segment.export(format="mp3").read())

    result = ""
    try:
        if settings.USE_CLOUD_WHISPER:
            result = await transcribe_cloud(fpath)
        else:
            raise Exception("Cloud Whisper ปิด")
    except Exception as e:
        logger.error(f"[❌] Cloud Whisper error: {e}")
        say("ขออภัยครับ Cloud Whisper มีปัญหา ผมจะลองแปลเองนะครับ")
        result = await asyncio.to_thread(transcribe_local, fpath)
    finally:
        try:
            os.remove(fpath)
        except:
            pass

    if not result:
        return ""

    logger.debug(f"[👂] ได้ยิน: {result}")

    # ตรวจสอบความถูกต้องของข้อความ
    if not await is_valid_transcript(result):
        logger.info("[🚫] ตัดข้อความที่ไม่เหมาะสมหรือเป็น noise")
        return ""

    return result
