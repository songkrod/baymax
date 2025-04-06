
from config.settings import settings
from openai import OpenAI
import tempfile

client = OpenAI(api_key=settings.OPENAI_API_KEY)

async def transcribe_audio(audio_bytes: bytes) -> str:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
        f.write(audio_bytes)
        f.flush()
        with open(f.name, "rb") as af:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=af,
                response_format="text"
            )
        return transcript
