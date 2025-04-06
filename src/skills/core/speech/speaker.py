
from services.tts.agent  import tts
from hardware.speaker import play_sound

def say(text: str):
    path = tts.speak(text)
    play_sound(path)
