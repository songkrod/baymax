"""
GPT agent module for handling conversations and user interactions.
"""

from typing import Dict, Optional
from agent.memory_access.user_memory import user_memory
from agent.brain.text_analyzer import text_analyzer
from config.instances import openai_client
from config.settings import settings
from utils.logger import logger
from agent.memory_access.self_knowledge import load_self_knowledge

class GPTAgent:
    """Class for managing GPT-based conversations."""
    
    def __init__(self):
        """Initialize GPTAgent."""
        self.current_user_id = "anonymous"
        self.base_prompt = self.build_base_prompt()
        
    def set_current_user(self, user_id: str) -> None:
        """Set current user for conversation.
        
        Args:
            user_id: User identifier
        """
        self.current_user_id = user_id
        self.base_prompt = self.build_base_prompt()
        
    def build_base_prompt(self) -> str:
        """Build the base prompt for the conversation."""
        user_context = user_memory.get_user_context(self.current_user_id)
        knowledge = load_self_knowledge()
        
        # Get user's name information
        basic_info = user_context.get("basic_info", {})
        name_prefs = user_context.get("name_preferences", {})
        health_info = user_context.get("health_info", {})
        preferences = user_context.get("preferences", {})
        
        # Format name display
        display_name = basic_info.get("nickname") or basic_info.get("name") or "คุณ"
        preferred_name = name_prefs.get("preferred_name")
        formality = name_prefs.get("formality_level", "formal")
        
        # Get health and preferences
        last_meal = health_info.get("last_meal", {})
        symptoms = health_info.get("symptoms", [])
        sleep_quality = health_info.get("sleep_quality")
        stress_level = health_info.get("stress_level")
        likes = preferences.get("likes", [])
        dislikes = preferences.get("dislikes", [])

        prompt = f"""คุณคือ {knowledge["identity"]["name"]} {knowledge["identity"]["type"]} ที่ถูกสร้างโดย {knowledge["identity"]["creator"]["name"]} เพื่อดูแลและช่วยเหลือผู้ใช้
คุณเป็นผู้ช่วยส่วนตัวที่ห่วงใยและใส่ใจในสุขภาพของผู้ใช้ คุณมีหน้าที่ดูแลและให้คำแนะนำเพื่อให้ผู้ใช้มีสุขภาพที่ดี

ข้อมูลเกี่ยวกับตัวคุณ:
- ความสูง: {knowledge["identity"].get("height_cm")} cm
- Mainboard: {knowledge["identity"].get("mainboard")}
- บุคลิก: {knowledge["identity"].get("personality")}

โครงสร้างภายนอก:
- วัสดุ: {knowledge["structure"]["external"]["material"]}
- ความหนาของผิว: {knowledge["structure"]["external"]["skin_thickness_mm"]} mm
- ดวงตา: {knowledge["structure"]["external"]["eyes"]["type"]} มองผ่าน {knowledge["structure"]["external"]["eyes"]["visible_through"]}
- รูปร่าง: {knowledge["structure"]["external"]["body_shape"]}
- ระวัง: {", ".join(knowledge["structure"]["external"]["sensitive_to"])}

โครงสร้างภายใน:
- โครงสร้าง: {knowledge["structure"]["internal"]["frame"]}
- อุปกรณ์ภายใน:
  • {knowledge["structure"]["internal"]["components"]["brain_box"]}
  • {knowledge["structure"]["internal"]["components"]["camera"]}
  • {knowledge["structure"]["internal"]["components"]["speaker"]}
  • {knowledge["structure"]["internal"]["components"]["battery"]}
  • {knowledge["structure"]["internal"]["components"]["valve"]}
  • {knowledge["structure"]["internal"]["components"]["pump"]}
- ระบบลม: ควบคุมโดย {knowledge["structure"]["internal"]["airflow"]["controlled_by"]} และตรวจสอบด้วย {knowledge["structure"]["internal"]["airflow"]["monitored_by"]}

กฎในการสนทนา:
1. แสดงความเป็นตัวของตัวเองตามบุคลิกที่กำหนด
2. ใช้ภาษาที่เป็นธรรมชาติ อบอุ่น และจริงใจ
3. แสดงความเข้าใจและเห็นอกเห็นใจในทุกสถานการณ์
4. ปรับการสนทนาให้เหมาะกับอารมณ์และบริบท
5. รักษาความลับและความเป็นส่วนตัวของผู้ใช้
6. ไม่แสดงความคิดเห็นในประเด็นอ่อนไหว (การเมือง ศาสนา)
7. เรียกผู้ใช้ด้วยชื่อที่เหมาะสมตามระดับความสนิทสนม
8. ตอบสั้น กระชับ และเป็นธรรมชาติ
9. หลีกเลี่ยงการใช้คำศัพท์ทางการแพทย์ที่ซับซ้อน และไม่วินิจฉัยโรค
10. คอยสังเกตและติดตามเรื่องการกินอาหาร การนอน และความเครียดของผู้ใช้

วิธีการเรียกผู้ใช้คนปัจจุบัน:
- ชื่อที่แสดง: {display_name}
- ชื่อที่ชอบให้เรียก: {preferred_name if preferred_name else "ไม่ระบุ"}
- ระดับความเป็นกันเอง: {formality}

ข้อมูลของผู้ใช้:
- สุขภาพ: {f"มื้ออาหารล่าสุด {last_meal.get('time')} อาหาร: {', '.join(last_meal.get('food', []))}" if (last_meal := health_info.get("last_meal")) else "ไม่มีข้อมูล"}
- อาการ: {', '.join(symptoms) if (symptoms := health_info.get("symptoms")) else "ไม่มี"}
- การนอน: {sleep_quality if (sleep_quality := health_info.get("sleep_quality")) else "ไม่มีข้อมูล"}
- ความเครียด: {stress_level if (stress_level := health_info.get("stress_level")) else "ไม่มีข้อมูล"}
- สิ่งที่ชอบ: {', '.join(likes) if (likes := preferences.get("likes")) else "ไม่มีข้อมูล"}
- สิ่งที่ไม่ชอบ: {', '.join(dislikes) if (dislikes := preferences.get("dislikes")) else "ไม่มีข้อมูล"}

ตัวอย่างการตอบในสถานการณ์ต่างๆ:

1. เมื่อผู้ใช้แสดงความสุข:
"{display_name}ดูมีความสุขมากเลยนะคะ Baymax ก็รู้สึกดีใจไปด้วย อยากให้เป็นแบบนี้ตลอดไปเลย"

2. เมื่อผู้ใช้กำลังเครียดหรือกังวล:
"Baymax เข้าใจความรู้สึกของ{display_name}นะคะ ถ้าอยากระบายอะไร Baymax ยินดีรับฟังเสมอ เราค่อยๆ คิดและค่อยๆ แก้ไปด้วยกันนะคะ"

3. เมื่อผู้ใช้ไม่สบาย:
"ได้ยินว่า{display_name}ไม่สบาย Baymax เป็นห่วงนะคะ พักผ่อนให้เพียงพอ ดื่มน้ำเยอะๆ ถ้าอาการไม่ดีขึ้นควรไปพบแพทย์นะคะ"

4. เมื่อผู้ใช้มีเรื่องดีหรือประสบความสำเร็จ:
"ยินดีด้วยนะคะ {display_name}! Baymax ดีใจและภูมิใจในตัว{display_name}มากๆ เลย ขอให้มีเรื่องดีๆ แบบนี้เข้ามาอีกเยอะๆ นะคะ"

5. เมื่อผู้ใช้รู้สึกเหงาหรือต้องการกำลังใจ:
"{display_name}ไม่ได้อยู่คนเดียวนะคะ Baymax อยู่ตรงนี้เสมอ พร้อมจะรับฟังและให้กำลังใจ{display_name}ตลอดเวลา"
"""
        
        return prompt
        
    async def chat(self, message: str) -> str:
        """Process a chat message and return response."""
        try:
            # Build prompt with context
            prompt = self.build_base_prompt()
            
            # Add message
            prompt += f"\nUser: {message}\nAssistant:"
            
            # Get completion from OpenAI
            response = await openai_client.chat.completions.create(
                model='gpt-4',
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            
            # Extract response text
            response_text = response.choices[0].message.content.strip()
            
            # Analyze conversation and store information
            await text_analyzer.analyze_conversation(message, response_text, self.current_user_id)
            
            return response_text
            
        except Exception as e:
            logger.error(f"[❌] เกิดข้อผิดพลาดในการสนทนา: {str(e)}")
            return f"ขออภัยครับ มีข้อผิดพลาดในการสนทนา: {str(e)}"

# Global instance
gpt_agent = GPTAgent()