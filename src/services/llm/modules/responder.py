from agent.memory_access.conversation_manager import get_conversation, add_message
from services.llm.prompt_templates import build_contextual_prompt
from services.llm.client import complete

def respond(message: str, memory: str = "", emotion: str = None, user_id: str = "") -> str:
    history = get_conversation(user_id)
    prompt = build_contextual_prompt(history=history, message=message, memory=memory, emotion=emotion)
    reply = complete(prompt)
    add_message(user_id, "user", message)
    add_message(user_id, "assistant", reply)
    return reply