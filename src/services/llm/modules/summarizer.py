from services.llm.client import complete

def summarize_conversation(messages: list[str]) -> str:
    prompt = "สรุปสิ่งที่ผู้ใช้พูดทั้งหมด: \n" + "\n".join(messages)
    return complete(prompt)