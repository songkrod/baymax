
import webrtcvad

vad = webrtcvad.Vad(3)
SAMPLE_RATE = 16000

def is_speech(frame: bytes) -> bool:
    return vad.is_speech(frame, SAMPLE_RATE)
