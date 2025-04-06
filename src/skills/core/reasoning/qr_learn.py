import requests
from agent.retriever.retriever import store_memory

def learn_from_url(url: str, user_id="self", source="qr_injected") -> str:
    """
    Download raw text from a URL and store each line into vector memory.

    ⚠️ รองรับเฉพาะ URL ที่ลิงก์ไปยังข้อความล้วน (text/plain), เช่น:
        - .txt (plain text)
        - .md (markdown)
        - .json (structured text)

    ❌ ไม่รองรับ PDF, ภาพ, หรือ binary file โดยตรง
    → หากต้องการอ่าน PDF ต้องแปลงเป็น text ล่วงหน้าก่อน (เช่น ผ่าน OCR หรือ pdf2text)
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        lines = response.text.splitlines()
        for line in lines:
            line = line.strip()
            if line:
                store_memory(
                    user_id=user_id,
                    text=line,
                    source=source,
                    tags=["learned"]
                )
        return "ผมเรียนรู้ข้อมูลจากลิงก์นี้เรียบร้อยแล้วครับ"
    except Exception as e:
        return f"ขออภัย ผมไม่สามารถโหลดข้อมูลจากลิงก์ได้: {e}"
