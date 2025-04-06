from .user_memory import UserMemoryManager
from .conversation_memory import ConversationMemory
from .name_memory import NameMemory
from .self_knowledge import SelfKnowledge
from .voice_memory import VoiceMemory
from agent.reasoning.voice_identity import VoiceIdentifier
from config.settings import settings

class MemoryManager:
    def __init__(self):
        self.user = UserMemoryManager()
        self.voice = VoiceMemory()
        self.name = NameMemory()
        self.self_knowledge = SelfKnowledge()
        self.voice_id = VoiceIdentifier()

    def init_user_if_not_exists(self, user_id: str, name: str = "ผู้ใช้ใหม่"):
        profile = self.user.get_user_profile(user_id)
        if not profile:
            self.user.update_user_profile(user_id, {
                "basic_info": {
                    "name": name,
                    "first_seen": "",
                    "last_seen": "",
                    "voice_samples": []
                },
                "preferences": {},
                "relationships": {}
            })

    def remember_conversation(self, conversation_id: str, user_id: str, role: str, content: str):
        self.conversation.log_message(conversation_id, role, content)

    def end_conversation(self, conversation_id: str, intent: str, refs: list[str]):
        self.conversation.end_conversation(conversation_id, intent, refs)

    def add_user_preference(self, user_id: str, item: str, like=True):
        self.user.add_preference(user_id, item, like)

    def get_self_description(self) -> str:
        data = self.self_knowledge.get_knowledge()
        name = data.get("name", settings.ROBOT_NAME)
        abilities = ", ".join(data.get("abilities", []))
        return f"ผมชื่อ {name} และสามารถทำสิ่งเหล่านี้ได้: {abilities}"

    def identify_or_create_user(self, embedding) -> str:
        user_id = self.voice_id.identify_user(embedding)
        if user_id is None:
            user_id = self.voice_id.register_new_user(embedding)
        self.init_user_if_not_exists(user_id)
        return user_id
