from faster_whisper import WhisperModel

model = WhisperModel("tiny", compute_type="int8")

def transcribe_local(audio_path: str) -> str:
    """
    ถอดเสียงจากไฟล์เสียงแบบ local โดยใช้ faster-whisper
    """
    try:
        segments, _ = model.transcribe(audio_path, beam_size=5)

        # รวมข้อความทั้งหมดจาก segment
        result = " ".join(segment.text.strip() for segment in segments if segment.text)
        return result.strip()
    except Exception as e:
        print(f"[Transcribe Error] {e}")
        return ""