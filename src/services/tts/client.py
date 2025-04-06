from config.settings import settings

# Auto select provider from settings
if settings.TTS_PROVIDER == "google":
    from services.tts.providers.google_tts import speak_text

else:
    raise ValueError(f"Unknown TTS provider: {settings.TTS_PROVIDER}")