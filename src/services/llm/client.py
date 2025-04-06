from config.settings import settings

# Auto select provider from settings
if settings.LLM_PROVIDER == "openai":
    from services.llm.providers.openai_llm import complete

else:
    raise ValueError(f"Unknown LLM provider: {settings.LLM_PROVIDER}")