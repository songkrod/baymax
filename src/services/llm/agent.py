from services.llm.modules import emotion, intent, summarizer, responder

class LLMAgent:
    def respond(self, message, memory="", emotion=None):
        if not emotion:
            emotion = self.detect_emotion(message)
        return responder.respond(message, memory, emotion)

    def detect_emotion(self, message):
        return emotion.detect_emotion(message)

    def classify_intent(self, message):
        return intent.classify_intent(message)

    def summarize(self, messages):
        return summarizer.summarize_conversation(messages)
    
llm = LLMAgent()