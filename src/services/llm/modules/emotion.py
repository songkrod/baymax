from services.llm.client import complete

EMOTION_PROMPT = """
คุณคือโมเดลวิเคราะห์อารมณ์...
"""

def detect_emotion(text: str) -> str:
    prompt = EMOTION_PROMPT.format(text=text.strip())
    return complete(prompt)