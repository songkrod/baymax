
import sounddevice as sd
import numpy as np
import asyncio
import tempfile
import soundfile as sf
from skills.core.listen.vad import is_speech
from utils.logger import logger
from skills.core.transcribe import get_transcriber

SAMPLE_RATE = 16000
CHANNELS = 1
FRAME_DURATION_MS = 30
FRAME_SIZE = int(SAMPLE_RATE * FRAME_DURATION_MS / 1000)
SILENCE_TIMEOUT_MS = 1000

async def record_audio_raw(timeout=7):
    logger.info("🔴 เริ่มบันทึกเสียง...")
    audio_buffer = []
    triggered = False
    silence_duration = 0
    recording_done = asyncio.Event()

    def callback(indata, frames, time, status):
        nonlocal triggered, silence_duration, audio_buffer
        frame = indata[:, 0].tobytes()
        if is_speech(frame):
            if not triggered:
                logger.info("🎤 ได้ยินเสียงแล้ว...")
            triggered = True
            silence_duration = 0
        elif triggered:
            silence_duration += FRAME_DURATION_MS
        if triggered:
            audio_buffer.append(indata.copy())
        if triggered and silence_duration > SILENCE_TIMEOUT_MS:
            recording_done.set()

    stream = sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype="int16",
        blocksize=FRAME_SIZE,
        callback=callback
    )

    with stream:
        try:
            await asyncio.wait_for(recording_done.wait(), timeout=timeout)
        except asyncio.TimeoutError:
            logger.info("[⏹️] หมดเวลาบันทึก")
    
    if not audio_buffer:
        return None

    audio = np.concatenate(audio_buffer, axis=0)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        sf.write(f.name, audio, SAMPLE_RATE)
        return open(f.name, "rb").read()

async def listen_and_transcribe():
    audio = await record_audio_raw()
    if not audio:
        return ""
    transcriber = get_transcriber()
    return await transcriber(audio)
