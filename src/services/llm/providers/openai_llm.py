import logging
from openai import OpenAI
from config.settings import settings

logger = logging.getLogger(__name__)

# Init OpenAI client
client = OpenAI(api_key=settings.OPENAI_API_KEY)

DEFAULT_MODEL = settings.GPT_MODEL or "gpt-3.5-turbo"

def complete(
    prompt: str,
    model: str = DEFAULT_MODEL,
    temperature: float = 0.7,
    max_tokens: int = 1024,
    system_prompt: str = None,
    debug: bool = False,
) -> str:
    """
    Low-level LLM call (OpenAI or future provider)
    Returns string response from GPT.
    """

    # Prepare message structure for ChatCompletion
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    try:
        if debug:
            logger.debug(f"[🔍 GPT Request] model={model}, prompt={prompt[:100]}...")

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        message = response.choices[0].message.content.strip()
        if debug:
            logger.debug(f"[🧠 GPT Response] {message[:100]}...")

        return message

    except Exception as e:
        logger.exception(f"[❌ GPT Error] {str(e)}")
        return "[ERROR] ไม่สามารถเชื่อมต่อกับ GPT ได้ในตอนนี้ครับ"