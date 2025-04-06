# src/agent/memory_access/self_knowledge_loader.py

import json
from agent.retriever.retriever import store_memory
from config.settings import settings

def preload_self_knowledge(path=settings.SELF_KNOWLEDGE_PATH):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    def add(text):
        store_memory(user_id="self", text=text, source="self_knowledge", tags=["self"])

    name = data.get("name", "Baymax")
    add(f"ผมชื่อ {name}")

    appearance = data.get("appearance", {})
    add(f"ผมมีลักษณะเป็นตัวพองสี {appearance.get('color')} ทำจาก {appearance.get('material')} และสูง {appearance.get('size')}")
    if "features" in appearance:
        for feature in appearance["features"]:
            add(f"ลักษณะเด่นของผมคือ {feature}")

    if "skin_material" in appearance:
        skin = appearance["skin_material"]
        add(f"ผิวของผมทำจาก TPU ความหนา {skin.get('main')}")
        add(f"แถบตาของผมทำจาก TPU สีดำโปร่งใส ความหนา {skin.get('eye_band')}")

    hardware = data.get("hardware", {})
    add("ผมควบคุมตัวเองด้วย " + hardware.get("main_processor", "ไมโครคอนโทรลเลอร์ไม่ทราบรุ่น"))

    for section, components in hardware.items():
        if isinstance(components, dict):
            for key, item in components.items():
                if isinstance(item, dict):
                    role = item.get("role")
                    location = item.get("location")
                    name = item.get("model") or item.get("type") or key
                    sentence = f"{name} อยู่ที่ {location} ใช้สำหรับ {role}" if role and location else f"ผมมี {name} ในระบบ"
                    add(sentence)
                elif isinstance(item, list):
                    for subitem in item:
                        if isinstance(subitem, dict):
                            role = subitem.get("role")
                            location = subitem.get("location")
                            name = subitem.get("model") or subitem.get("type") or key
                            sentence = f"{name} อยู่ที่ {location} ใช้สำหรับ {role}" if role and location else f"ผมมี {name} ในระบบ"
                            add(sentence)
                elif isinstance(item, str):
                    add(f"{key} ของผมคือ {item}")

    for ability in data.get("abilities", []):
        store_memory(user_id="self", text=f"ผมสามารถ {ability}", source="self_knowledge", tags=["self", "ability"])

    for limit in data.get("limitations", []):
        store_memory(user_id="self", text=f"ข้อจำกัดของผมคือ {limit}", source="self_knowledge", tags=["self", "limitation"])
