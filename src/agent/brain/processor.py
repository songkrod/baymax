import json
from typing import Dict, List
from agent.brain.gpt_agent import gpt_agent
from skills.core.speech.speaker import say
from utils.logger import logger
from skills.core.listen.recognizer import voice_recognizer

async def process_command(text: str) -> None:
    """Process voice command.
    
    Args:
        text: Transcribed text from voice
    """
    # Process command with voice recognizer
    response = await voice_recognizer.process_command(text)
    
    # Speak response
    say(response)
    logger.info(f"[🤖] {response}")


async def get_user_conversation_history(user_id: str) -> str:
    """Get conversation history for a user.
    
    Args:
        user_id: User ID to get history for
        
    Returns:
        Formatted conversation history
    """
    conversations = list_conversations(user_id)
    if not conversations:
        return "ไม่พบประวัติการสนทนา"
        
    history = []
    for conv in conversations:
        history.append(f"เวลา: {conv['start_time']}")
        if conv.get('final_intent'):
            history.append(f"Intent: {conv['final_intent']}")
        history.append(f"จำนวนข้อความ: {conv['message_count']}")
        history.append("---")
        
    return "\n".join(history)