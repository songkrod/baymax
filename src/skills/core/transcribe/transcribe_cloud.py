
from services.asr.agent import asr

async def transcribe_cloud(audio_bytes: bytes) -> str:
    return await asr.transcribe(audio_bytes)
