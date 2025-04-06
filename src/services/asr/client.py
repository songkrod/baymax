from config.settings import settings

# Auto select provider from settings
if settings.ASR_PROVIDER == "whisper":
    from services.asr.providers.whisper_asr import transcribe_audio

else:
    raise ValueError(f"Unknown ASR provider: {settings.ASR_PROVIDER}")