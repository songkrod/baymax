from services.llm.client import complete

INTENT_LABELS = [
    "command",
    "question",
    "greeting",
    "confirmation",
    "rejection",
    "unknown",
    "clarification",
    "call_robot",
    "maybe_call_robot"
]

INTENT_PROMPT = """
คุณมีหน้าที่วิเคราะห์เจตนาผู้ใช้จากข้อความภาษาไทย
จงเลือกเจตนา (intent) จากรายการต่อไปนี้ และตอบเป็น **คำภาษาอังกฤษเท่านั้น** ตาม keyword:
{labels}

ห้ามแปล หรือเพิ่มคำอธิบายใด ๆ ตอบเฉพาะคำเดียว

ตัวอย่าง:
- ถ้าผู้ใช้ทักทาย → ตอบว่า greeting
- ถ้าผู้ใช้สั่งงาน → ตอบว่า command
- ถ้าผู้ใช้ปฏิเสธ → ตอบว่า rejection

ข้อความ: "{{text}}"
intent:
""".replace("{labels}", ", ".join(INTENT_LABELS))

def classify_intent(text: str) -> str:
    prompt = INTENT_PROMPT.format(text=text.strip())
    return complete(prompt).lower().strip()
