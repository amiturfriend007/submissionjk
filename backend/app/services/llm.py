from abc import ABC, abstractmethod
from typing import Any
import json

import httpx

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
        prompt = (
            "Summarize the following book content in 6-8 concise bullet points. "
            "Focus on plot, themes, style, and key takeaways.\n\n"
            f"{text}"
        )
        response = await _ollama_generate(prompt)
        return _clean_text(response) or _fallback_summary(text)

    async def analyze_sentiment(self, text: str) -> dict[str, Any]:
        prompt = (
            "Analyze the sentiment of this review. "
            "Return ONLY JSON object with keys: score (float from -1 to 1), "
            "label (positive|neutral|negative), rationale (short string).\n\n"
            f"Review:\n{text}"
        )
        response = await _ollama_generate(prompt)
        parsed = _parse_sentiment_json(response)
        if parsed:
            return parsed
        return _heuristic_sentiment(text)


async def _ollama_generate(prompt: str) -> str:
    payload = {
        "model": settings.llm_model,
        "prompt": prompt,
        "stream": False,
    }
    timeout = httpx.Timeout(settings.llm_timeout_seconds)
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.post(f"{settings.llm_url}/api/generate", json=payload)
        resp.raise_for_status()
        data = resp.json()
        return data.get("response", "")


async def ollama_status() -> dict[str, Any]:
    timeout = httpx.Timeout(settings.llm_timeout_seconds)
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.get(f"{settings.llm_url}/api/tags")
        resp.raise_for_status()
        data = resp.json()
        models = [m.get("name") for m in data.get("models", []) if m.get("name")]
        configured = settings.llm_model
        configured_ready = any(
            name == configured or name.startswith(f"{configured}:") for name in models
        )
        return {
            "connected": True,
            "configured_model": configured,
            "configured_model_ready": configured_ready,
            "available_models": models,
        }


async def ollama_chat(messages: list[dict[str, str]]) -> str:
    payload = {
        "model": settings.llm_model,
        "messages": messages,
        "stream": False,
    }
    timeout = httpx.Timeout(settings.llm_timeout_seconds)
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.post(f"{settings.llm_url}/api/chat", json=payload)
        resp.raise_for_status()
        data = resp.json()
        message = data.get("message", {})
        return (message.get("content") or "").strip()


def _clean_text(value: str) -> str:
    return (value or "").strip()


def _fallback_summary(text: str) -> str:
    cleaned = (text or "").strip()
    if not cleaned:
        return "No textual content available to summarize."
    excerpt = cleaned[:500]
    return f"Summary unavailable from LLM. Text excerpt: {excerpt}"


def _parse_sentiment_json(response: str) -> dict[str, Any] | None:
    raw = (response or "").strip()
    if not raw:
        return None
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        start = raw.find("{")
        end = raw.rfind("}")
        if start == -1 or end == -1 or end <= start:
            return None
        try:
            parsed = json.loads(raw[start : end + 1])
        except json.JSONDecodeError:
            return None

    score = parsed.get("score")
    label = parsed.get("label")
    rationale = parsed.get("rationale", "")
    if not isinstance(score, (int, float)) or not isinstance(label, str):
        return None
    score = max(-1.0, min(1.0, float(score)))
    label = label.lower().strip()
    if label not in {"positive", "neutral", "negative"}:
        label = "neutral"
    return {"score": score, "label": label, "rationale": str(rationale)}


def _heuristic_sentiment(text: str) -> dict[str, Any]:
    t = (text or "").lower()
    if not t.strip():
        return {"score": 0.0, "label": "neutral", "rationale": "empty review"}
    positive_terms = ["great", "excellent", "love", "good", "amazing", "insightful"]
    negative_terms = ["bad", "poor", "boring", "hate", "terrible", "awful"]
    pos = sum(1 for term in positive_terms if term in t)
    neg = sum(1 for term in negative_terms if term in t)
    if pos > neg:
        return {"score": min(1.0, 0.25 + 0.15 * pos), "label": "positive", "rationale": "keyword signal"}
    if neg > pos:
        return {"score": max(-1.0, -0.25 - 0.15 * neg), "label": "negative", "rationale": "keyword signal"}
    return {"score": 0.0, "label": "neutral", "rationale": "balanced keyword signal"}


def get_llm() -> LLMProvider:
    if settings.llm_provider in {"local", "ollama"}:
        return LocalLLM()
    # elif settings.llm_provider == "openai":
    #     return OpenAILLM(...)
    raise NotImplementedError(f"Unknown llm provider {settings.llm_provider}")
