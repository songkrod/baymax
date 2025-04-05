from config.settings import settings
from pydub import AudioSegment
from pydub.playback import play

def play_sound(file_path):
    print(f"เล่นเสียงจาก {file_path}")

    sound = AudioSegment.from_file(file_path, format="mp3")
    play(sound)