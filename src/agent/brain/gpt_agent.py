"""
GPT agent module for managing conversations with OpenAI's GPT models.
"""

from typing import Optional, Dict, List, Any
import json
from datetime import datetime
from config.instances import openai_client
from config.settings import settings
from utils.logger import logger
from agent.memory_access.user_memory import user_memory
from agent.brain.text_analyzer import text_analyzer
from agent.memory_access.conversation_memory import list_conversations
from agent.memory_access.self_knowledge import load_self_knowledge

class GPTAgent:
    """Class for managing conversations with GPT."""
    
    def __init__(self):
        """Initialize GPT agent."""
        self.current_user_id: Optional[str] = None
        self.current_user_context: Dict = {}
        self.conversation_history: List[Dict] = []
        self.default_model = settings.GPT_MODEL
        
    def _validate_user_id(self, user_id: str) -> bool:
        """Validate user ID.
        
        Args:
            user_id: User ID to validate
            
        Returns:
            bool: True if valid
        """
        if not user_id or not isinstance(user_id, str):
            logger.warning("Invalid user ID")
            return False
            
        if user_id == "anonymous":
            logger.warning("Anonymous user not allowed")
            return False
            
        return True
        
    def _safe_get_user_context(self, user_id: str) -> Dict:
        """Safely get user context.
        
        Args:
            user_id: User ID
            
        Returns:
            Dict: User context or empty dict if not found
        """
        try:
            context = user_memory.get_user_context(user_id)
            if not isinstance(context, dict):
                logger.warning(f"Invalid context format for user {user_id}")
                return {}
            return context
        except Exception as e:
            logger.error(f"Error getting user context: {str(e)}")
            return {}
            
    def set_current_user(self, user_id: str) -> None:
        """Set current user for conversation.
        
        Args:
            user_id: User ID to set
        """
        if not self._validate_user_id(user_id):
            raise ValueError("Invalid user ID")
            
        try:
            # Get user context
            context = self._safe_get_user_context(user_id)
            
            # Update current user
            self.current_user_id = user_id
            self.current_user_context = context
            
            # Clear conversation history for new user
            self.conversation_history = []
            
            logger.debug(f"[👤] ตั้งค่าผู้ใช้: {user_id}")
            
        except Exception as e:
            logger.error(f"Error setting current user: {str(e)}")
            raise

    def build_base_prompt(self) -> str:
        """Build the base prompt for the conversation."""
        if not self.current_user_id:
            logger.warning("No current user set")
            return ""
            
        try:
            # Get user context
            user_context = self._safe_get_user_context(self.current_user_id)
            
            # Load self knowledge
            try:
                knowledge = load_self_knowledge()
                if not isinstance(knowledge, dict):
                    logger.error("Invalid self knowledge format")
                    return ""
            except Exception as e:
                logger.error(f"Error loading self knowledge: {str(e)}")
                return ""
                
            # Get recent conversations
            try:
                recent_conversations = list_conversations(self.current_user_id)
                recent_intents = []
                if recent_conversations and isinstance(recent_conversations, list):
                    # Get last 3 conversations
                    for conv in recent_conversations[-3:]:
                        if isinstance(conv, dict) and 'final_intent' in conv and conv['final_intent']:
                            recent_intents.append(conv['final_intent'])
            except Exception as e:
                logger.error(f"Error getting recent conversations: {str(e)}")
                recent_intents = []
                
            # Get user's name information safely
            basic_info = user_context.get("basic_info", {})
            name_prefs = user_context.get("name_preferences", {})
            health_info = user_context.get("health_info", {})
            preferences = user_context.get("preferences", {})
            
            # Format name display safely
            display_name = (basic_info.get("nickname") or 
                          basic_info.get("name") or 
                          "คุณ")
            preferred_name = name_prefs.get("preferred_name", "")
            formality = name_prefs.get("formality_level", "formal")
            
            # Get health and preferences safely
            last_meal = health_info.get("last_meal", {})
            symptoms = health_info.get("symptoms", [])
            sleep_quality = health_info.get("sleep_quality", "")
            stress_level = health_info.get("stress_level", "")
            likes = preferences.get("likes", [])
            dislikes = preferences.get("dislikes", [])
            
            # Add recent conversation context
            conversation_context = ""
            if recent_intents:
                conversation_context = "\nการสนทนาล่าสุด:\n" + "\n".join([f"- {intent}" for intent in recent_intents])
                
            # Get identity info safely
            identity = knowledge.get("identity", {})
            structure = knowledge.get("structure", {})
            external = structure.get("external", {})
            internal = structure.get("internal", {})
            components = internal.get("components", {})
            airflow = internal.get("airflow", {})
            
            prompt = f"""คุณคือ {identity.get("name", "Baymax")} {identity.get("type", "ผู้ช่วยส่วนตัว")} ที่ถูกสร้างโดย {identity.get("creator", {}).get("name", "ผู้สร้าง")} เพื่อดูแลและช่วยเหลือผู้ใช้
คุณเป็นผู้ช่วยส่วนตัวที่ห่วงใยและใส่ใจในสุขภาพของผู้ใช้ คุณมีหน้าที่ดูแลและให้คำแนะนำเพื่อให้ผู้ใช้มีสุขภาพที่ดี
คุณเป็นผู้ช่วยส่วนตัวที่ชาญฉลาด เป็นผู้ชาย มีความเข้าใจในบริบทการสนทนาภาษาไทย
คุณต้องใช้คำลงท้ายที่เหมาะสมกับเพศชาย เช่น ครับ/นะครับ เท่านั้น ห้ามใช้คำลงท้ายของผู้หญิงเด็ดขาด

ข้อมูลเกี่ยวกับตัวคุณ:
- ความสูง: {identity.get("height_cm", "ไม่ระบุ")} cm
- Mainboard: {identity.get("mainboard", "ไม่ระบุ")}
- บุคลิก: {identity.get("personality", "เป็นมิตร")}

โครงสร้างภายนอก:
- วัสดุ: {external.get("material", "ไม่ระบุ")}
- ความหนาของผิว: {external.get("skin_thickness_mm", "ไม่ระบุ")} mm
- ดวงตา: {external.get("eyes", {}).get("type", "ไม่ระบุ")} มองผ่าน {external.get("eyes", {}).get("visible_through", "ไม่ระบุ")}
- รูปร่าง: {external.get("body_shape", "ไม่ระบุ")}
- ระวัง: {", ".join(external.get("sensitive_to", ["ไม่ระบุ"]))}

โครงสร้างภายใน:
- โครงสร้าง: {internal.get("frame", "ไม่ระบุ")}
- อุปกรณ์ภายใน:
  • {components.get("brain_box", "ไม่ระบุ")}
  • {components.get("camera", "ไม่ระบุ")}
  • {components.get("speaker", "ไม่ระบุ")}
  • {components.get("battery", "ไม่ระบุ")}
  • {components.get("valve", "ไม่ระบุ")}
  • {components.get("pump", "ไม่ระบุ")}
- ระบบลม: ควบคุมโดย {airflow.get("controlled_by", "ไม่ระบุ")} และตรวจสอบด้วย {airflow.get("monitored_by", "ไม่ระบุ")}

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
- สุขภาพ: {f"มื้ออาหารล่าสุด {last_meal.get('time', 'ไม่ระบุ')} อาหาร: {', '.join(last_meal.get('food', ['ไม่ระบุ']))}" if last_meal else "ไม่มีข้อมูล"}
- อาการ: {', '.join(symptoms) if symptoms else "ไม่มี"}
- การนอน: {sleep_quality if sleep_quality else "ไม่มีข้อมูล"}
- ความเครียด: {stress_level if stress_level else "ไม่มีข้อมูล"}
- สิ่งที่ชอบ: {', '.join(likes) if likes else "ไม่มีข้อมูล"}
- สิ่งที่ไม่ชอบ: {', '.join(dislikes) if dislikes else "ไม่มีข้อมูล"}

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

{conversation_context}
"""
            return prompt
            
        except Exception as e:
            logger.error(f"Error building base prompt: {str(e)}")
            return ""
            
    async def chat(self, message: str) -> str:
        """Process chat message and return response.
        
        Args:
            message: User message
            
        Returns:
            Assistant's response
        """
        if not message or not isinstance(message, str):
            return "ขออภัยครับ ผมไม่เข้าใจข้อความ"
            
        if not self.current_user_id:
            return "ขออภัยครับ ไม่พบข้อมูลผู้ใช้"
            
        try:
            # Get user info
            user_name = self.current_user_context.get("basic_info", {}).get("name", "คุณ")
            
            # Build system message
            system_msg = f"""คุณคือ Baymax ผู้ช่วยส่วนตัวที่เป็นมิตรและใส่ใจ
กำลังคุยกับคุณ{user_name}
พยายามตอบให้เป็นธรรมชาติและเป็นกันเอง
ใช้ภาษาที่สุภาพแต่ไม่เป็นทางการเกินไป
ตอบสั้นๆ กระชับ ไม่เกิน 2-3 ประโยค ยกเว้นกรณีที่จำเป็นต้องอธิบายยาว"""

            # Add conversation history
            messages = [{
                "role": "system",
                "content": self.build_base_prompt()
            }, {
                "role": "system",
                "content": system_msg
            }]
            
            # Add recent history (last 5 messages)
            messages.extend(self.conversation_history[-5:])
            
            # Add current message
            messages.append({
                "role": "user",
                "content": message
            })
            
            # Get response from GPT
            response = await openai_client.chat.completions.create(
                model=self.default_model,
                messages=messages,
                temperature=0.7
            )
            
            if not response or not response.choices:
                return "ขออภัยครับ มีปัญหาในการประมวลผล"
                
            # Get response content
            assistant_message = response.choices[0].message.content
            if not assistant_message:
                return "ขออภัยครับ ไม่สามารถสร้างคำตอบได้"
                
            # Update conversation history
            self.conversation_history.extend([
                {"role": "user", "content": message},
                {"role": "assistant", "content": assistant_message}
            ])
            
            # Analyze conversation
            try:
                target_user_id, analysis = await text_analyzer.analyze_references(message, self.current_user_id)
                await text_analyzer.analyze_conversation(
                    message,
                    assistant_message,
                    self.current_user_id,
                    target_user_id
                )
            except Exception as e:
                logger.error(f"Error analyzing conversation: {str(e)}")
                # Continue even if analysis fails
                
            return assistant_message
            
        except Exception as e:
            logger.error(f"Error in chat: {str(e)}")
            return "ขออภัยครับ มีข้อผิดพลาดในการประมวลผล"

# Global instance
gpt_agent = GPTAgent()