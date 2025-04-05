"""
Shared instances across the application.
"""

from openai import AsyncOpenAI
from config.settings import settings

# Create shared OpenAI client instance
openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY) 