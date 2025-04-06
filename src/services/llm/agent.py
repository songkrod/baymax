# src/services/llm/agent.py

from services.llm.modules import emotion, intent, summarizer, responder

class LLMAgent:
    def respond_no_tracking(self, message, memory="", emotion=None, user_id=""):
        if not emotion:
            emotion = self.detect_emotion(message)
        reply = responder.respond(message, memory, emotion, user_id=user_id)
        return reply
    
    def respond(self, message, memory="", emotion=None, user_id=""):
        from agent.tracker.conversation_tracker import track_conversation
        reply = self.respond_no_tracking(message, memory, emotion, user_id)
        track_conversation(user_id, message, reply, emotion)
        return reply

    def detect_emotion(self, message):
        return emotion.detect_emotion(message)

    def classify_intent(self, message):
        return intent.classify_intent(message)

    def summarize(self, messages):
        return summarizer.summarize_conversation(messages)

llm = LLMAgent()