from services.llm.client import complete

INTENT_PROMPT = """
คุณมีหน้าที่วิเคราะห์เจตนาผู้ใช้...
"""

def classify_intent(text: str) -> str:
    prompt = INTENT_PROMPT.format(text=text.strip())
    return complete(prompt)