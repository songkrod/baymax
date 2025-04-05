import numpy as np
import io
import soundfile as sf
from faster_whisper import WhisperModel
from config.settings import settings

# โหลดโมเดลครั้งเดียว
model = WhisperModel(
    settings.WHISPER_MODEL,
    device="cpu",
    compute_type="int8"
)

def transcribe_local(audio_array_or_path, samplerate=16000) -> str:
    """
    รองรับทั้งไฟล์เสียง และ np.ndarray (เสียงจาก memory)
    """
    segments = []

    if isinstance(audio_array_or_path, np.ndarray):
        buf = io.BytesIO()
        sf.write(buf, audio_array_or_path, samplerate, format="WAV")
        buf.seek(0)
        segments, _info = model.transcribe(buf, beam_size=5)
    else:
        segments, _info = model.transcribe(audio_array_or_path, beam_size=5)

    text = "".join(segment.text for segment in segments).strip()
    return text