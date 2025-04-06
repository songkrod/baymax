from services.llm.client import complete

EMOTION_LABELS = [
    "happy",
    "sad",
    "angry",
    "relaxed",
    "stressed",
    "neutral"
]

EMOTION_PROMPT = """
คุณคือโมเดลวิเคราะห์อารมณ์จากข้อความภาษาไทย
หน้าที่ของคุณคือระบุอารมณ์ของผู้พูด โดยเลือกจากรายการด้านล่าง และตอบเป็น keyword ภาษาอังกฤษ 1 คำเท่านั้น:
{labels}

ห้ามแปล ห้ามเพิ่มคำอธิบาย และห้ามตอบภาษาไทย

ข้อความ: "{{text}}"
อารมณ์:
""".replace("{labels}", ", ".join(EMOTION_LABELS))

def detect_emotion(text: str) -> str:
    prompt = EMOTION_PROMPT.format(text=text.strip())
    return complete(prompt).lower().strip()
