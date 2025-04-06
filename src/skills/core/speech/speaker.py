
from services.tts import speak_text
from hardware.speaker import play_sound

def say(text: str):
    path = speak_text(text)
    play_sound(path)
