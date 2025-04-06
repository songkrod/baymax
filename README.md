# Baymax Mini

Baymax Mini เป็นผู้ช่วยอัจฉริยะที่สามารถโต้ตอบด้วยเสียงภาษาไทย พร้อมความสามารถในการจดจำเสียงและเรียนรู้บริบทการสนทนา

## ความสามารถหลัก

- 🎤 **รู้จำเสียงพูด**: ใช้ Whisper สำหรับแปลงเสียงพูดเป็นข้อความ รองรับทั้งแบบ local และ cloud
- 🗣️ **พูดโต้ตอบ**: ใช้ Google TTS สำหรับการพูดตอบกลับด้วยเสียงที่เป็นธรรมชาติ พร้อมระบบแบ่งข้อความยาวอัตโนมัติ
- 👥 **จดจำผู้ใช้**: ใช้ Resemblyzer สำหรับจดจำเสียงของผู้ใช้แต่ละคน
- 🧠 **เข้าใจบริบท**: วิเคราะห์และจดจำบริบทการสนทนา ความชอบ และความสัมพันธ์ของผู้ใช้
- 🤖 **GPT-4**: ใช้ GPT-4 ในการวิเคราะห์และสร้างการตอบสนองที่ฉลาดและเป็นธรรมชาติ

## การติดตั้ง

1. ติดตั้ง dependencies:

```bash
pip install -r requirements.txt
```

2. ตั้งค่า environment variables ใน `.env`:

```env
OPENAI_API_KEY=your_openai_api_key
GOOGLE_APPLICATION_CREDENTIALS=path/to/google_credentials.json
```

3. สร้างโฟลเดอร์ที่จำเป็น:

```bash
mkdir -p data/{caches,logs,memories,voices/{embeddings,samples}}
```

## การใช้งาน

1. เริ่มต้นใช้งาน:

```bash
python src/main.py
```

2. เรียกใช้ Baymax โดยพูดชื่อ (ค่าเริ่มต้น: "baymax")

3. พูดคุยได้ตามต้องการ Baymax จะ:
   - จดจำเสียงของคุณ
   - เก็บบันทึกบริบทการสนทนา
   - ตอบกลับอย่างฉลาดและเป็นธรรมชาติ
   - แบ่งข้อความยาวเป็นชิ้นเล็กๆ เพื่อการพูดที่ราบรื่น

## โครงสร้างโปรเจค

```
src/
├── agent/              # โมดูลหลักสำหรับการประมวลผล
│   ├── brain/         # ตรรกะการทำงานหลัก
│   └── memory_access/ # การจัดการความจำ
├── config/             # การตั้งค่าระบบ
├── skills/            # ความสามารถต่างๆ
│   └── core/         # ความสามารถพื้นฐาน
│       ├── speech/   # การพูดและ TTS
│       └── listen/   # การฟังและ STT
└── utils/             # ฟังก์ชันช่วยเหลือ
```

## การพัฒนา

1. เพิ่มความสามารถใหม่:

   - สร้างไฟล์ใน `src/skills/`
   - ลงทะเบียนใน `config/settings.py`

2. ปรับแต่งการตอบสนอง:
   - แก้ไข prompts ใน `agent/brain/`
   - ปรับปรุงการวิเคราะห์ใน `text_analyzer.py`
   - ปรับแต่งการพูดใน `skills/core/speech/speaker.py`

## ผู้พัฒนา

- **Songkrod Thanavorn (Toomtam)**
  - GitHub: [@songkrod](https://github.com/songkrod)

## License

MIT License
