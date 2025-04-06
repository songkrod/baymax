from services.tts.client import speak_text

class TTSService:
    def speak(self, text: str, output_path="output.mp3"):
        return speak_text(text, output_path)
    
tts = TTSService()