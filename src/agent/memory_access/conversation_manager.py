conversations = {}

LIMIT_CONVERSATION = 10

def add_message(user_id: str, role: str, text: str):
    conversations.setdefault(user_id, []).append({"role": role, "text": text})
    if len(conversations[user_id]) > LIMIT_CONVERSATION:
        conversations[user_id] = conversations[user_id][-LIMIT_CONVERSATION:]

def get_conversation(user_id: str):
    return conversations.get(user_id, [])


def clear_conversation(user_id: str):
    conversations.pop(user_id, None)