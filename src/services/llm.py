
from config.settings import settings
from openai import OpenAI

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def complete(prompt: str, model=settings.GPT_MODEL) -> str:
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content.strip()
