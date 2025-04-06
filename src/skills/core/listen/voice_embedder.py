
from resemblyzer import VoiceEncoder
import numpy as np
import tempfile
import soundfile as sf

encoder = VoiceEncoder()

def extract_embedding(audio_bytes: bytes) -> list[float]:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        f.write(audio_bytes)
        f.flush()
        wav, sr = sf.read(f.name)
        emb = encoder.embed_utterance(wav)
        return emb.tolist()
