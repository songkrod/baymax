from services.llm import complete

EMOTION_CLASSIFIER_PROMPT = """
คุณคือนักวิเคราะห์ข้อความภาษาไทย
หน้าที่ของคุณคือระบุอารมณ์ของผู้พูด โดยดูจากเนื้อหาที่เขาพูด
ให้ตอบแค่อารมณ์หลักคำเดียว เช่น:
- เศร้า
- เครียด
- หงุดหงิด
- ดีใจ
- สบายใจ
ถ้าระบุไม่ได้ให้ตอบว่า: ไม่แน่ใจ

ข้อความ: "{text}"
อารมณ์ของผู้พูดคือ:
"""

def detect_emotion(text: str) -> str:
    prompt = EMOTION_CLASSIFIER_PROMPT.format(text=text.strip())
    result = complete(prompt)
    return result.split()[0]  # เอาคำแรกพอ เช่น "เศร้า"