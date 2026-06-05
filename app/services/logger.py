# app/services/logger.py
from app.database import AsyncSession
from app.models.request_log import RequestLog

async def log_request(api_key: str, result: dict, status: str, error: str = None):
    async with AsyncSession() as session:
        log = RequestLog(
            api_key       = api_key,
            model         = result.get("model"),
            provider      = result.get("provider"),
            prompt_hash   = result.get("prompt_hash"),
            input_tokens  = result.get("input_tokens", 0),
            output_tokens = result.get("output_tokens", 0),
            latency_ms    = result.get("latency_ms", 0),
            cost_usd      = 0.0,   # free tier
            status        = status,
            error         = error,
        )
        session.add(log)
        await session.commit()