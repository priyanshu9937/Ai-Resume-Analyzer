from app.core.config import get_settings
from app.services.llm import GeminiProvider


def get_llm_provider() -> GeminiProvider:
    return GeminiProvider(get_settings())
