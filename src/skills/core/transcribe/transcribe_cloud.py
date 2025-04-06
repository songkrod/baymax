
from services.asr import transcribe_audio

async def transcribe_cloud(audio_bytes: bytes) -> str:
    return await transcribe_audio(audio_bytes)
