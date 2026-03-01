from typing import Literal

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.config import settings
from app.services.llm import ollama_chat, ollama_status

router = APIRouter()


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str = Field(min_length=1)


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(min_length=1)


@router.get("/status")
async def llm_connectivity_status():
    try:
        result = await ollama_status()
        result["llm_url"] = settings.llm_url
        result["llm_provider"] = settings.llm_provider
        return result
    except Exception as exc:
        return {
            "connected": False,
            "llm_url": settings.llm_url,
            "llm_provider": settings.llm_provider,
            "configured_model": settings.llm_model,
            "configured_model_ready": False,
            "available_models": [],
            "error": str(exc),
        }


@router.post("/chat")
async def llm_chat(payload: ChatRequest):
    messages = [{"role": m.role, "content": m.content.strip()} for m in payload.messages]
    try:
        answer = await ollama_chat(messages)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"LLM upstream error: {exc}") from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"LLM chat failed: {exc}") from exc

    if not answer:
        raise HTTPException(status_code=502, detail="LLM returned an empty response")
    return {"answer": answer}
