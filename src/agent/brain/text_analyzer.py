"""
Text analyzer module for processing and analyzing text content.
"""

from typing import Dict, Optional, List, Tuple
import json
from pathlib import Path
from config.instances import openai_client
from config.settings import settings
from agent.memory_access.user_memory import user_memory
from agent.memory_access.name_memory import load_name_memory, add_name_to_memory
from utils.logger import logger
from rapidfuzz import fuzz, process
from skills.core.speech.speaker import say
from skills.core.listen.listener import record_and_transcribe

class TextAnalyzer:
    """Class for analyzing text content."""
    
    def __init__(self):
        """Initialize text analyzer."""
        pass
        
    async def analyze_conversation(
        self,
        user_message: str,
        assistant_message: str,
        user_id: str,
        target_user_id: Optional[str] = None
    ) -> None:
        """Analyze conversation and store extracted information.
        
        Args:
            user_message: Message from user
            assistant_message: Response from assistant
            user_id: ID of the user to store information for
            target_user_id: Optional ID of user being discussed
        """
        if user_id == "anonymous":
            return
            
        try:
            # Analyze conversation with GPT
            analysis_prompt = f"""วิเคราะห์บทสนทนาต่อไปนี้และสรุปข้อมูลสำคัญเกี่ยวกับผู้ใช้และบุคคลที่ถูกกล่าวถึง:

ผู้ใช้: {user_message}
ผู้ช่วย: {assistant_message}

โปรดวิเคราะห์และส่งผลลัพธ์ในรูปแบบ JSON ที่มีโครงสร้างดังนี้:
{{
    "current_user": {{
        "basic_info": {{
            "name": "ชื่อที่พบในบทสนทนา (ถ้ามี)",
            "nickname": "ชื่อเล่นที่พบในบทสนทนา (ถ้ามี)"
        }},
        "aliases": ["คำที่ใช้เรียกตัวเอง หรือถูกเรียก เช่น พี่ น้อง คุณ"],
        "name_preferences": {{
            "preferred_name": "ชื่อที่ชอบให้เรียก (ถ้ามี)",
            "formality_level": "ระดับความเป็นกันเอง (formal/informal/friendly)"
        }},
        "health_info": {{
            "last_meal": {{
                "time": "เวลาที่ทานอาหารมื้อล่าสุด (ถ้ามี)",
                "food": ["รายการอาหารที่ทาน"],
                "is_healthy": true/false
            }},
            "symptoms": ["อาการเจ็บป่วยที่พบในบทสนทนา"],
            "sleep_quality": "คุณภาพการนอน (good/fair/poor) ถ้ามีการพูดถึง",
            "stress_level": "ระดับความเครียด (low/medium/high) ถ้ามีการพูดถึง"
        }},
        "preferences": {{
            "likes": ["สิ่งที่ชอบที่พบในบทสนทนา"],
            "dislikes": ["สิ่งที่ไม่ชอบที่พบในบทสนทนา"],
            "favorite_foods": ["อาหารที่ชอบ"],
            "food_restrictions": ["ข้อจำกัดในการทานอาหาร"]
        }},
        "relationships": {{
            "partner": "user_id ของคู่รัก (ถ้ามีการพูดถึง)",
            "family": ["user_id ของสมาชิกครอบครัว (ถ้ามีการพูดถึง)"]
        }}
    }},
    "mentioned_person": {{
        "basic_info": {{
            "name": "ชื่อของบุคคลที่ถูกกล่าวถึง (ถ้ามี)",
            "nickname": "ชื่อเล่นของบุคคลที่ถูกกล่าวถึง (ถ้ามี)"
        }},
        "aliases": ["คำที่ใช้เรียกบุคคลที่ถูกกล่าวถึง เช่น ที่รัก babe น้อง พี่"],
        "name_preferences": {{
            "preferred_name": "ชื่อที่ชอบให้เรียก (ถ้ามี)",
            "formality_level": "ระดับความเป็นกันเอง (formal/informal/friendly)"
        }},
        "health_info": {{
            "last_meal": {{
                "time": "เวลาที่ทานอาหารมื้อล่าสุด (ถ้ามี)",
                "food": ["รายการอาหารที่ทาน"],
                "is_healthy": true/false
            }},
            "symptoms": ["อาการเจ็บป่วยที่พบในบทสนทนา"],
            "sleep_quality": "คุณภาพการนอน (good/fair/poor) ถ้ามีการพูดถึง",
            "stress_level": "ระดับความเครียด (low/medium/high) ถ้ามีการพูดถึง"
        }},
        "preferences": {{
            "likes": ["สิ่งที่ชอบที่พบในบทสนทนา"],
            "dislikes": ["สิ่งที่ไม่ชอบที่พบในบทสนทนา"],
            "favorite_foods": ["อาหารที่ชอบ"],
            "food_restrictions": ["ข้อจำกัดในการทานอาหาร"]
        }},
        "relationships": {{
            "partner": "user_id ของคู่รัก (ถ้ามีการพูดถึง)",
            "family": ["user_id ของสมาชิกครอบครัว (ถ้ามีการพูดถึง)"]
        }}
    }}
}}"""

            response = await openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "คุณเป็นผู้เชี่ยวชาญในการวิเคราะห์บทสนทนาและสกัดข้อมูลสำคัญ"},
                    {"role": "user", "content": analysis_prompt}
                ]
            )
            
            # Parse analysis results
            try:
                analysis = json.loads(response.choices[0].message.content)
            except json.JSONDecodeError:
                return
                
            # Update current user's information
            if current_user := analysis.get("current_user"):
                if basic_info := current_user.get("basic_info"):
                    if any(basic_info.values()):
                        user_memory.update_memory("basic_info", basic_info, user_id)
                        
                if aliases := current_user.get("aliases"):
                    if aliases:
                        user_memory.update_memory("aliases", aliases, user_id)
                        
                if name_prefs := current_user.get("name_preferences"):
                    if any(name_prefs.values()):
                        user_memory.update_memory("name_preferences", name_prefs, user_id)
                        
                if health_info := current_user.get("health_info"):
                    if any(health_info.values()):
                        user_memory.update_memory("health_info", health_info, user_id)
                        
                if preferences := current_user.get("preferences"):
                    if any(preferences.values()):
                        user_memory.update_memory("preferences", preferences, user_id)
                        
                if relationships := current_user.get("relationships"):
                    if any(relationships.values()):
                        user_memory.update_memory("relationships", relationships, user_id)
                        
            # Update mentioned person's information if target_user_id exists
            if target_user_id and (mentioned_person := analysis.get("mentioned_person")):
                if basic_info := mentioned_person.get("basic_info"):
                    if any(basic_info.values()):
                        user_memory.update_memory("basic_info", basic_info, target_user_id)
                        
                if aliases := mentioned_person.get("aliases"):
                    if aliases:
                        user_memory.update_memory("aliases", aliases, target_user_id)
                        
                if name_prefs := mentioned_person.get("name_preferences"):
                    if any(name_prefs.values()):
                        user_memory.update_memory("name_preferences", name_prefs, target_user_id)
                        
                if health_info := mentioned_person.get("health_info"):
                    if any(health_info.values()):
                        user_memory.update_memory("health_info", health_info, target_user_id)
                        
                if preferences := mentioned_person.get("preferences"):
                    if any(preferences.values()):
                        user_memory.update_memory("preferences", preferences, target_user_id)
                        
                if relationships := mentioned_person.get("relationships"):
                    if any(relationships.values()):
                        user_memory.update_memory("relationships", relationships, target_user_id)
                        
            # Store interaction
            user_memory.add_interaction("chat", {
                "user_message": user_message,
                "assistant_message": assistant_message,
                "target_user_id": target_user_id
            }, user_id)
            
        except Exception:
            # Silently fail if analysis fails
            pass
            
    async def analyze_references(self, user_message: str, current_user_id: str) -> Tuple[Optional[str], Dict]:
        """Analyze message to find references to other users.
        
        Args:
            user_message: Message from user
            current_user_id: Current user ID
            
        Returns:
            Tuple of (target_user_id, analysis_result)
        """
        if current_user_id == "anonymous":
            return None, {}
            
        try:
            # Use GPT to analyze references in the message
            analysis_prompt = f"""วิเคราะห์ประโยคต่อไปนี้และระบุว่ามีการอ้างถึงบุคคลอื่นหรือไม่:

"{user_message}"

โปรดวิเคราะห์และส่งผลลัพธ์ในรูปแบบ JSON ที่มีโครงสร้างดังนี้:
{{
    "references": [
        {{
            "text": "คำหรือวลีที่ใช้อ้างถึง (เช่น เขา แฟน ที่รัก)",
            "type": "ประเภทความสัมพันธ์ (partner/family/friend)",
            "context": "บริบทที่แสดงว่าเป็นการอ้างถึงคนเดียวกัน"
        }}
    ],
    "is_same_person": true/false,
    "explanation": "คำอธิบายว่าทำไมจึงคิดว่าเป็นการอ้างถึงคนเดียวกันหรือคนละคน"
}}"""

            response = await openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "คุณเป็นผู้เชี่ยวชาญในการวิเคราะห์การอ้างอิงถึงบุคคลในบทสนทนา"},
                    {"role": "user", "content": analysis_prompt}
                ]
            )
            
            # Get content from the new response structure
            content = response.choices[0].message.content
            if not content:
                return None, {}
                
            analysis = json.loads(content)
            
            # If no references found
            if not analysis.get("references"):
                return None, analysis
                
            # Get current user's context
            user_context = user_memory.get_user_context(current_user_id)
            target_user_id = None
            
            # Check each reference
            for ref in analysis["references"]:
                if ref["type"] == "partner":
                    # Check existing partner
                    if partner_id := user_context.get("relationships", {}).get("partner"):
                        target_user_id = partner_id
                        break
                    # Create temporary user for new partner
                    else:
                        target_user_id = user_memory.create_temporary_user({
                            "relationships": {"partner": current_user_id}
                        })
                        user_memory.update_memory("relationships", {
                            "partner": target_user_id
                        }, current_user_id)
                        break
                        
                # Try to find by alias
                elif found_id := user_memory.find_user_by_alias(ref["text"], current_user_id):
                    target_user_id = found_id
                    break
                    
            return target_user_id, analysis
            
        except Exception as e:
            print(f"Error analyzing references: {str(e)}")
            return None, {}
            
    async def extract_name(self, text: str) -> Optional[str]:
        """Extract name from introduction text.
        
        Args:
            text: Text containing name introduction
            
        Returns:
            Extracted name if found, None otherwise
        """
        prompt = f"""
        จากข้อความแนะนำตัว: "{text}"
        
        ช่วยดึงชื่อของผู้พูดออกมา โดย:
        1. ถ้าเจอชื่อให้ตอบเฉพาะชื่อ
        2. ถ้าไม่เจอชื่อให้ตอบ null
        3. ถ้าเจอหลายชื่อให้เลือกชื่อที่น่าจะเป็นชื่อของผู้พูดมากที่สุด
        4. ตัดคำนำหน้าออก เช่น คุณ, นาย, นางสาว
        
        ตอบเป็น JSON format เท่านั้น:
        {{"name": "ชื่อที่พบ หรือ null"}}
        """
        
        response = await openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{
                "role": "system",
                "content": "You are a helpful assistant that extracts names from Thai text."
            }, {
                "role": "user",
                "content": prompt
            }]
        )
        
        try:
            result = response.choices[0].message.content
            name = json.loads(result)["name"]
            return name if name != "null" else None
        except:
            return None
            
    async def detect_wake_word(self, text: str, should_ask: bool = True) -> Tuple[bool, Optional[str]]:
        """Detect wake word in text and learn new variations.
        
        Args:
            text: Text to check for wake word
            should_ask: Whether to ask user about uncertain matches
            
        Returns:
            Tuple of (is_wake_word, matched_name)
        """
        name_memory = load_name_memory()
        
        # Convert to lowercase for case-insensitive matching
        text = text.lower()
        words = text.split()
        
        # Add main name from settings to name memory
        all_names = name_memory + [settings.ROBOT_NAME.lower()]
        
        # Check each word
        for word in words:
            # Find best match
            best_match = process.extractOne(
                word,
                all_names,
                scorer=fuzz.ratio,
                score_cutoff=80
            )
            
            if best_match:
                matched_name = best_match[0]
                score = best_match[1]
                logger.debug(f"[🔍] พบคำที่ใกล้เคียง: '{word}' -> '{matched_name}' (score: {score})")
                return True, matched_name
                
            # Check uncertain matches
            uncertain_match = process.extractOne(
                word,
                all_names,
                scorer=fuzz.ratio,
                score_cutoff=60
            )
            
            if uncertain_match and should_ask:
                matched_name = uncertain_match[0]
                score = uncertain_match[1]
                logger.debug(f"[❓] พบคำที่อาจจะเป็นชื่อ: '{word}' -> '{matched_name}' (score: {score})")
                say(f"คำว่า '{word}' เป็นการเรียกชื่อผมใช่ไหมครับ?")
                
                # Wait for response
                response = await record_and_transcribe()
                
                # Use GPT to analyze intent
                is_confirmed = await self.is_confirmation(response, f"ผู้ใช้ถูกถามว่าคำว่า '{word}' เป็นการเรียกชื่อหุ่นยนต์หรือไม่")
                if is_confirmed:
                    add_name_to_memory(word)
                    return True, word
        
        return False, None
        
    async def is_confirmation(self, text: str, context: str) -> bool:
        """Check if text is a confirmation.
        
        Args:
            text: Text to analyze
            context: Context of the question
            
        Returns:
            True if text is a confirmation, False otherwise
        """
        prompt = f"""
        บริบท: {context}
        คำตอบของผู้ใช้: "{text}"
        
        วิเคราะห์ว่าคำตอบเป็นการยืนยัน (ใช่/ถูกต้อง) หรือปฏิเสธ
        
        ตอบเป็น JSON format เท่านั้น:
        {{"is_confirmation": true/false}}
        """
        
        response = await openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{
                "role": "system",
                "content": "You are a helpful assistant that analyzes confirmation intent in Thai text. Always respond in JSON format."
            }, {
                "role": "user",
                "content": prompt
            }]
        )
        
        try:
            result = response.choices[0].message.content
            return json.loads(result)["is_confirmation"]
        except:
            return False

# Global instance
text_analyzer = TextAnalyzer() 