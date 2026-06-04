# app/routers/chat.py
from fastapi import APIRouter, HTTPException, Header, Depends
from pydantic import BaseModel
from redis.asyncio import Redis
from app.providers.huggingface import HuggingFaceProvider
from app.services.rate_limiter import RateLimiter
from app.services.logger import log_request
from app.config import settings

router   = APIRouter()
provider = HuggingFaceProvider()

class ChatRequest(BaseModel):
    messages:   list[dict]
    model:      str | None = None
    max_tokens: int = 512

@router.post("/chat")
async def chat(
    req: ChatRequest,
    x_api_key: str = Header(default="dev-key"),
):
    redis = Redis.from_url(settings.redis_url, decode_responses=True)
    limiter = RateLimiter(redis)

    allowed, remaining = await limiter.check(x_api_key)
    if not allowed:
        raise HTTPException(429, detail="Rate limit exceeded. Try again in 60s.")

    # Fallback chain across available models
    models_to_try = [req.model] if req.model else provider.models
    last_error = None

    for model in models_to_try:
        try:
            result = await provider.complete(req.messages, model, req.max_tokens)
            await log_request(api_key=x_api_key, result=result, status="success")
            return {
                "text":          result["text"],
                "model":         result["model"],
                "usage": {
                    "input_tokens":  result["input_tokens"],
                    "output_tokens": result["output_tokens"],
                },
                "latency_ms":    round(result["latency_ms"], 2),
                "rate_limit_remaining": remaining,
            }
        except Exception as e:
            last_error = str(e)
            await log_request(api_key=x_api_key, result={"model": model, "provider": "huggingface",
                "input_tokens": 0, "output_tokens": 0, "latency_ms": 0,
                "prompt_hash": ""}, status="error", error=last_error)
            continue

    raise HTTPException(503, detail=f"All models failed. Last error: {last_error}")