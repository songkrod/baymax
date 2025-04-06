# ✅ โครงสร้างใหม่ที่ชัดเจนของ src/agent/brain/

# เราแบ่งตามหน้าที่ของแต่ละส่วนใน Brain ดังนี้:

# ┌────────────┐ ┌────────────┐ ┌────────────┐

# │ Processor │ --> │ Interpreter│ --> │ Reasoner │

# └────────────┘ └────────────┘ └────────────┘

# ฟัง/แปลงเสียง วิเคราะห์ intent วางแผน/ตัดสินใจ

# ------------------------------------------------------------------

# ✅ processor.py: รับเสียง → แปลงเป็นข้อความ + speaker + cleaned info

# "Pre-processing ชั้นล่างสุด"

# > รู้ว่าใครพูด, พูดว่าอะไร, มาจากเสียงไหน

# ✅ interpreter.py: วิเคราะห์ text + metadata → กลายเป็น intent

# "แปลงคำพูดเป็นเจตนา + context"

# > เช่น intent = "call_robot", "ask_weather", "say_hello"

# ✅ reasoner/\*.py: ตัดสินใจตาม intent + memory + สภาพปัจจุบัน

# "คิดว่าจะทำอะไร"

# > เช่น ถ้า intent = call_robot และยังไม่ตื่น → ให้ปลุกตัวเอง

# > ถ้า intent = ask_weather → ไปดึง weather + ตอบกลับ

# ------------------------------------------------------------------

# ✅ สิ่งที่ควรอยู่ในแต่ละไฟล์:

# 📄 processor.py

# - def process_audio(audio_bytes): → return { text, user_id, ... }

# - (ควรไม่รวม wake word logic)

# 📄 interpreter.py

# - def interpret(text, user_id): return { intent, context, confidence }

# - ใช้ name_reasoner เพื่อวิเคราะห์ชื่อหุ่น

# - อนาคตอาจใช้ GPT เพื่อตีความ intent ก็ได้

# 📄 reasoner/\*

# - name_reasoner.py → จัดการชื่อที่ใช้เรียกหุ่น

# - intent_reasoner.py → แยก action ตาม intent

# - emotion_reasoner.py → วิเคราะห์ความรู้สึกในบทสนทนา

# - memory_reasoner.py → ใช้ความจำเก่า/สถานะร่วมประกอบ

# ------------------------------------------------------------------

# ✅ agent.py (หรือ main flow)

# - ไม่ควรวิเคราะห์ intent เอง

# - ทำแค่เรียก processor → interpreter → reasoner → act

# ------------------------------------------------------------------

# ✅ ไฟล์ที่ควรมีใน src/agent/brain/

# agent/brain/

# ├── processor.py # รับเสียง วิเคราะห์ speaker/text

# ├── interpreter.py # แปลง text เป็น intent/context

# └── **init**.py

# และ reasoner แยกอยู่ที่:

# agent/reasoner/

# ├── name_reasoner.py

# ├── intent_reasoner.py

# └── ...

# ------------------------------------------------------------------

# ❌ ไม่ควรมีอีก:

# - wake_word_reasoner.py → ย้าย logic ไปที่ name_reasoner.py แล้ว

# - processor ที่ทำหน้าที่วิเคราะห์ชื่อ → ตัดออกไปไว้ reasoner/interpreter

# ------------------------------------------------------------------

# ✅ ประโยชน์ของการแยกแบบนี้:

# - ทำให้แต่ละ layer มีหน้าที่ชัดเจน (SRP: Single Responsibility Principle)

# - ทดสอบและ reuse แต่ละส่วนได้ง่าย

# - รองรับการต่อ GPT, memory, plugin, action ได้ไม่ปวดหัว

# - agent.py สั้นลง และอ่านง่ายมาก
