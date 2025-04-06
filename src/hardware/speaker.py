from config.settings import settings
from pydub import AudioSegment
from pydub.playback import play
from utils.logger import logger

def play_sound(file_path):
    logger.info(f"[📛] เล่นเสียงจาก {file_path}")

    sound = AudioSegment.from_file(file_path, format="mp3")
    play(sound)