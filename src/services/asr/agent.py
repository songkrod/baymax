from services.asr.client import transcribe_audio

class ASRAgent:
    def transcribe(self, audio_bytes: bytes) -> str:
        return transcribe_audio(audio_bytes)
    
asr = ASRAgent()