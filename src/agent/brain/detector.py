"""
Wake word detection module.
"""

from config.settings import settings
from utils.logger import logger
from agent.memory_access.name_memory import load_name_memory, add_name_to_memory
from rapidfuzz import fuzz, process
from skills.core.speech.speaker import say
from agent.brain.gpt_agent import gpt_agent
from typing import Tuple, Optional
from agent.brain.text_analyzer import text_analyzer

async def detect_and_learn_name(text: str, should_ask: bool = True) -> Tuple[bool, Optional[str]]:
    """Detect wake word in text and learn new variations.
    
    Args:
        text: Text to check for wake word
        should_ask: Whether to ask user about uncertain matches
        
    Returns:
        Tuple of (is_wake_word, matched_name)
    """
    return await text_analyzer.detect_wake_word(text, should_ask)

async def is_wake_word(text: str) -> bool:
    """Check if text contains wake word.
    
    Args:
        text: Text to check
        
    Returns:
        True if wake word found, False otherwise
    """
    is_called, _ = await detect_and_learn_name(text)
    return is_called 