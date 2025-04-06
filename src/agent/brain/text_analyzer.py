"""
Text analyzer module for processing and analyzing text content.
"""

from typing import Dict, Optional, List, Tuple, Any
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
from agent.memory_access.conversation_memory import add_conversation, list_conversations
from datetime import datetime

class TextAnalyzer:
    """Class for analyzing text content."""
    
    def __init__(self):
        """Initialize text analyzer."""
        self.default_sections = [
            ("basic_info", {}),
            ("aliases", []),
            ("name_preferences", {}),
            ("health_info", {}),
            ("preferences", {}),
            ("relationships", {})
        ]
        
    def _validate_response(self, response: Any) -> bool:
        """Validate OpenAI API response.
        
        Args:
            response: Response from OpenAI API
            
        Returns:
            bool: True if response is valid
        """
        if not response:
            logger.warning("Empty response from OpenAI API")
            return False
            
        if not hasattr(response, 'choices'):
            logger.warning("Response missing choices attribute")
            return False
            
        if not response.choices:
            logger.warning("Response has empty choices")
            return False
            
        if not hasattr(response.choices[0], 'message'):
            logger.warning("First choice missing message attribute")
            return False
            
        if not hasattr(response.choices[0].message, 'content'):
            logger.warning("Message missing content attribute")
            return False
            
        return True
        
    def _safe_get_content(self, response: Any) -> Optional[str]:
        """Safely get content from OpenAI API response.
        
        Args:
            response: Response from OpenAI API
            
        Returns:
            Optional[str]: Content if valid, None otherwise
        """
        try:
            if not self._validate_response(response):
                return None
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error getting content from response: {str(e)}")
            return None
            
    def _safe_parse_json(self, content: str) -> Optional[Dict]:
        """Safely parse JSON content.
        
        Args:
            content: JSON string to parse
            
        Returns:
            Optional[Dict]: Parsed JSON if valid, None otherwise
        """
        if not content or not isinstance(content, str):
            return None
            
        try:
            data = json.loads(content)
            if not isinstance(data, dict):
                logger.warning("Parsed JSON is not a dictionary")
                return None
            return data
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON: {str(e)}")
            return None
            
    def _safe_update_memory(self, section_name: str, section_data: Any, user_id: str) -> None:
        """Safely update user memory.
        
        Args:
            section_name: Name of section to update
            section_data: Data to update with
            user_id: User ID to update
        """
        try:
            if not user_id or user_id == "anonymous":
                return
                
            if section_name == "aliases":
                if section_data and isinstance(section_data, list):
                    user_memory.update_memory(section_name, section_data, user_id)
            else:
                if section_data and isinstance(section_data, dict) and any(section_data.values()):
                    user_memory.update_memory(section_name, section_data, user_id)
        except Exception as e:
            logger.error(f"Error updating memory for section {section_name}: {str(e)}")
            
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
        if not user_message or not assistant_message or not user_id or user_id == "anonymous":
            return
            
        try:
            # Get recent conversations for context
            recent_conversations = list_conversations(user_id) or []
            recent_messages = []
            
            if recent_conversations and len(recent_conversations) > 0:
                # Get messages from last conversation
                last_conv = recent_conversations[-1]
                if last_conv and isinstance(last_conv, dict):
                    recent_messages = last_conv.get("messages", [])
            
            # Add current messages
            messages = [
                {"role": "user", "content": user_message, "timestamp": datetime.now().isoformat()},
                {"role": "assistant", "content": assistant_message, "timestamp": datetime.now().isoformat()}
            ]
            
            # Store conversation with context
            final_intent = None
            try:
                if len(recent_messages) > 0:
                    # If we have previous messages, analyze the full context
                    all_messages = recent_messages + messages
                    final_intent = await self.analyze_intent(all_messages)
            except Exception as e:
                logger.error(f"Error analyzing intent: {str(e)}")
                final_intent = None
            
            # Add conversation first to avoid delay
            add_conversation(messages, user_id, final_intent)
            
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

            try:
                response = await openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",  # Use faster model
                    messages=[
                        {"role": "system", "content": "คุณเป็นผู้เชี่ยวชาญในการวิเคราะห์บทสนทนาและสกัดข้อมูลสำคัญ"},
                        {"role": "user", "content": analysis_prompt}
                    ],
                    temperature=0  # Make it more deterministic
                )
                
                content = self._safe_get_content(response)
                if not content:
                    return
                    
                # Parse analysis results
                analysis = self._safe_parse_json(content)
                if not analysis:
                    return
                    
                # Update current user's information
                current_user = analysis.get("current_user", {})
                if not isinstance(current_user, dict):
                    current_user = {}
                    
                # Update each section safely
                for section_name, default_value in self.default_sections:
                    section_data = current_user.get(section_name, default_value)
                    self._safe_update_memory(section_name, section_data, user_id)
                    
                # Update mentioned person's information if target_user_id exists
                if target_user_id:
                    mentioned_person = analysis.get("mentioned_person", {})
                    if not isinstance(mentioned_person, dict):
                        mentioned_person = {}
                        
                    # Update each section safely for mentioned person
                    for section_name, default_value in self.default_sections:
                        section_data = mentioned_person.get(section_name, default_value)
                        self._safe_update_memory(section_name, section_data, target_user_id)
                        
                # Store interaction
                try:
                    user_memory.add_interaction("chat", {
                        "user_message": user_message,
                        "assistant_message": assistant_message,
                        "target_user_id": target_user_id
                    }, user_id)
                except Exception as e:
                    logger.error(f"Error storing interaction: {str(e)}")
                
            except Exception as e:
                logger.error(f"Error in conversation analysis: {str(e)}")
                # Continue execution even if analysis fails
                
        except Exception as e:
            logger.error(f"Error in analyze_conversation: {str(e)}")
            # Continue execution even if outer block fails
            
    async def analyze_references(self, user_message: str, current_user_id: str) -> Tuple[Optional[str], Dict]:
        """Analyze message to find references to other users.
        
        Args:
            user_message: Message from user
            current_user_id: Current user ID
            
        Returns:
            Tuple of (target_user_id, analysis_result)
        """
        if not user_message or not isinstance(user_message, str) or not current_user_id or current_user_id == "anonymous":
            return None, {}
            
        try:
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
                model="gpt-3.5-turbo",  # Use faster model
                messages=[
                    {"role": "system", "content": "คุณเป็นผู้เชี่ยวชาญในการวิเคราะห์การอ้างอิงถึงบุคคลในบทสนทนา"},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0  # Make it more deterministic
            )
            
            content = self._safe_get_content(response)
            if not content:
                return None, {}
                
            analysis = self._safe_parse_json(content)
            if not analysis:
                return None, {}
                
            # If no references found
            if not analysis.get("references"):
                return None, analysis
                
            # Get current user's context
            try:
                user_context = user_memory.get_user_context(current_user_id)
                if not isinstance(user_context, dict):
                    logger.warning(f"Invalid user context for user {current_user_id}")
                    return None, analysis
            except Exception as e:
                logger.error(f"Error getting user context: {str(e)}")
                return None, analysis
                
            target_user_id = None
            
            # Check each reference
            for ref in analysis.get("references", []):
                if not isinstance(ref, dict):
                    continue
                    
                ref_type = ref.get("type")
                ref_text = ref.get("text")
                
                if not ref_type or not ref_text:
                    continue
                    
                if ref_type == "partner":
                    try:
                        # Check existing partner
                        relationships = user_context.get("relationships", {})
                        if isinstance(relationships, dict):
                            partner_id = relationships.get("partner")
                            if partner_id:
                                target_user_id = partner_id
                                break
                            # Create temporary user for new partner
                            else:
                                target_user_id = user_memory.create_temporary_user({
                                    "relationships": {"partner": current_user_id}
                                })
                                if target_user_id:
                                    user_memory.update_memory("relationships", {
                                        "partner": target_user_id
                                    }, current_user_id)
                                    break
                    except Exception as e:
                        logger.error(f"Error handling partner reference: {str(e)}")
                        continue
                        
                # Try to find by alias
                try:
                    if found_id := user_memory.find_user_by_alias(ref_text, current_user_id):
                        target_user_id = found_id
                        break
                except Exception as e:
                    logger.error(f"Error finding user by alias: {str(e)}")
                    continue
                    
            return target_user_id, analysis
            
        except Exception as e:
            logger.error(f"Error analyzing references: {str(e)}")
            return None, {}
            
    async def extract_name(self, text: str) -> Optional[str]:
        """Extract name from introduction text.
        
        Args:
            text: Text containing name introduction
            
        Returns:
            Extracted name if found, None otherwise
        """
        if not text or not isinstance(text, str):
            logger.warning("Invalid input for name extraction")
            return None
            
        try:
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
                model="gpt-3.5-turbo",
                messages=[{
                    "role": "system",
                    "content": "You are a helpful assistant that extracts names from Thai text. Always respond in valid JSON format."
                }, {
                    "role": "user",
                    "content": prompt
                }],
                temperature=0
            )
            
            content = self._safe_get_content(response)
            if not content:
                logger.warning("No content returned from name extraction")
                return None
                
            result = self._safe_parse_json(content)
            if not result:
                logger.warning("Failed to parse name extraction result")
                return None
                
            name = result.get("name")
            if not name or name == "null" or not isinstance(name, str):
                logger.info("No valid name found in text")
                return None
                
            # Clean and validate the extracted name
            cleaned_name = name.strip()
            if not cleaned_name or len(cleaned_name) < 2:  # Assume names are at least 2 chars
                logger.warning("Extracted name too short or empty")
                return None
                
            return cleaned_name
            
        except Exception as e:
            logger.error(f"Error in name extraction: {str(e)}")
            return None
            
    async def detect_wake_word(self, text: str, should_ask: bool = True) -> Tuple[bool, Optional[str]]:
        """Detect wake word in text and learn new variations.
        
        Args:
            text: Text to check for wake word
            should_ask: Whether to ask user about uncertain matches
            
        Returns:
            Tuple of (is_wake_word, matched_name)
        """
        if not text or not isinstance(text, str):
            return False, None
            
        try:
            name_memory = load_name_memory()
            if not isinstance(name_memory, list):
                logger.warning("Invalid name memory format")
                name_memory = []
                
            # Convert to lowercase for case-insensitive matching
            text = text.lower().strip()
            if not text:
                return False, None
                
            words = text.split()
            if not words:
                return False, None
                
            # Add main name from settings to name memory
            robot_name = settings.ROBOT_NAME.lower() if settings.ROBOT_NAME else ""
            if robot_name:
                all_names = name_memory + [robot_name]
            else:
                all_names = name_memory
                
            if not all_names:
                return False, None
                
            # Check each word
            for word in words:
                if not word:
                    continue
                    
                try:
                    # Find best match
                    best_match = process.extractOne(
                        word,
                        all_names,
                        scorer=fuzz.ratio,
                        score_cutoff=80
                    )
                    
                    if best_match and len(best_match) >= 2:
                        matched_name = best_match[0]
                        score = best_match[1]
                        logger.debug(f"[🔍] พบคำที่ใกล้เคียง: '{word}' -> '{matched_name}' (score: {score})")
                        return True, matched_name
                        
                    # Check uncertain matches
                    if should_ask:
                        uncertain_match = process.extractOne(
                            word,
                            all_names,
                            scorer=fuzz.ratio,
                            score_cutoff=60
                        )
                        
                        if uncertain_match and len(uncertain_match) >= 2:
                            matched_name = uncertain_match[0]
                            score = uncertain_match[1]
                            logger.debug(f"[❓] พบคำที่อาจจะเป็นชื่อ: '{word}' -> '{matched_name}' (score: {score})")
                            
                            try:
                                say(f"คำว่า '{word}' เป็นการเรียกชื่อผมใช่ไหมครับ?")
                                
                                # Wait for response
                                response = await record_and_transcribe()
                                if not response:
                                    continue
                                    
                                # Use GPT to analyze intent
                                is_confirmed = await self.is_confirmation(
                                    response,
                                    f"ผู้ใช้ถูกถามว่าคำว่า '{word}' เป็นการเรียกชื่อหุ่นยนต์หรือไม่"
                                )
                                
                                if is_confirmed:
                                    try:
                                        add_name_to_memory(word)
                                        return True, word
                                    except Exception as e:
                                        logger.error(f"Error adding name to memory: {str(e)}")
                                        continue
                                        
                            except Exception as e:
                                logger.error(f"Error in confirmation flow: {str(e)}")
                                continue
                                
                except Exception as e:
                    logger.error(f"Error processing word '{word}': {str(e)}")
                    continue
            
            return False, None
            
        except Exception as e:
            logger.error(f"Error in wake word detection: {str(e)}")
            return False, None
            
    async def is_confirmation(self, text: str, context: str) -> bool:
        """Check if text is a confirmation.
        
        Args:
            text: Text to analyze
            context: Context of the question
            
        Returns:
            True if text is a confirmation, False otherwise
        """
        if not text or not isinstance(text, str) or not context or not isinstance(context, str):
            return False
            
        try:
            prompt = f"""
            บริบท: {context}
            คำตอบของผู้ใช้: "{text}"
            
            วิเคราะห์ว่าคำตอบเป็นการยืนยัน (ใช่/ถูกต้อง) หรือปฏิเสธ
            
            ตอบเป็น JSON format เท่านั้น:
            {{"is_confirmation": true/false}}
            """
            
            response = await openai_client.chat.completions.create(
                model="gpt-3.5-turbo",  # Use faster model
                messages=[{
                    "role": "system",
                    "content": "You are a helpful assistant that analyzes confirmation intent in Thai text. Always respond in JSON format."
                }, {
                    "role": "user",
                    "content": prompt
                }],
                temperature=0  # Make it more deterministic
            )
            
            content = self._safe_get_content(response)
            if not content:
                return False
                
            result = self._safe_parse_json(content)
            if not result:
                return False
                
            return bool(result.get("is_confirmation", False))
            
        except Exception as e:
            logger.error(f"Error in confirmation analysis: {str(e)}")
            return False
            
    async def analyze_intent(self, messages: List[Dict]) -> Optional[Dict]:
        """Analyze intent from conversation history.
        
        Args:
            messages: List of conversation messages
            
        Returns:
            Dict or None if analysis fails
        """
        if not messages or not isinstance(messages, list):
            logger.warning("Invalid messages format for intent analysis")
            return None
        
        try:
            # Build conversation text
            conversation_lines = []
            for msg in messages:
                if not isinstance(msg, dict):
                    continue
                    
                role = msg.get('role', 'unknown')
                content = msg.get('content', '')
                
                if not content:
                    continue
                    
                conversation_lines.append(f"{role}: {content}")
                
            conversation_text = "\n".join(conversation_lines)
            if not conversation_text.strip():
                logger.warning("Empty conversation text for intent analysis")
                return None
            
            prompt = f"""วิเคราะห์บทสนทนาต่อไปนี้และระบุ intent ที่แท้จริง:

{conversation_text}

ตอบในรูปแบบ JSON:
{{
    "intent": "ชื่อ intent ที่เหมาะสมเป็นภาษาอังกฤษเท่านั้น",
    "confidence": 0.0 ถึง 1.0,
    "explanation": "คำอธิบายว่าทำไมจึงคิดว่าเป็น intent นี้"
}}"""

            response = await openai_client.chat.completions.create(
                model="gpt-3.5-turbo",  # Use faster model
                messages=[{
                    "role": "system",
                    "content": "คุณเป็นผู้เชี่ยวชาญในการวิเคราะห์ intent จากบทสนทนาภาษาไทย"
                }, {
                    "role": "user",
                    "content": prompt
                }],
                temperature=0  # Make it more deterministic
            )
            
            content = self._safe_get_content(response)
            if not content:
                return None
                
            result = self._safe_parse_json(content)
            if not result:
                return None
                
            confidence = float(result.get("confidence", 0))
            if confidence >= 0.7:
                return {
                    "intent": result.get("intent", "unknown"),
                    "confidence": confidence,
                    "explanation": result.get("explanation", "")
                }
            else:
                logger.info(f"Low confidence intent analysis: {confidence}")
                return None
            
        except Exception as e:
            logger.error(f"Error in intent analysis: {str(e)}")
            return None

# Global instance
text_analyzer = TextAnalyzer() 