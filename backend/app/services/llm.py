from abc import ABC, abstractmethod
from typing import Any

from app.core.config import settings


class LLMProvider(ABC):
    @abstractmethod
    async def summarize(self, text: str) -> str:
        pass

    @abstractmethod
    async def analyze_sentiment(self, text: str) -> dict[str, Any]:
        pass


class LocalLLM(LLMProvider):
    async def summarize(self, text: str) -> str:
        # stub: return first 200 chars
        return text[:200] + "..."

    async def analyze_sentiment(self, text: str) -> dict[str, Any]:
        # simple polarity stub
        return {"score": 0.0, "label": "neutral"}


def get_llm() -> LLMProvider:
    if settings.llm_provider == "local":
        return LocalLLM()
    # elif settings.llm_provider == "openai":
    #     return OpenAILLM(...)
    raise NotImplementedError(f"Unknown llm provider {settings.llm_provider}")