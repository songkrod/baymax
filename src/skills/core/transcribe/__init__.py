
from config.settings import settings
from skills.core.transcribe.transcribe_cloud import transcribe_cloud
from skills.core.transcribe.transcribe_local import transcribe_local

def get_transcriber():
    if settings.USE_CLOUD_WHISPER:
        return transcribe_cloud
    return transcribe_local