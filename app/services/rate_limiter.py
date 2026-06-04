# app/services/rate_limiter.py
import time, uuid
from redis.asyncio import Redis
from app.config import settings

class RateLimiter:
    def __init__(self, redis: Redis):
        self.redis = redis
        self.window = 60          # seconds
        self.limit  = settings.rate_limit_rpm

    async def check(self, api_key: str) -> tuple[bool, int]:
        now    = time.time()
        key    = f"rl:{api_key}"
        cutoff = now - self.window

        async with self.redis.pipeline(transaction=True) as pipe:
            pipe.zremrangebyscore(key, 0, cutoff)
            pipe.zcard(key)
            pipe.zadd(key, {str(uuid.uuid4()): now})
            pipe.expire(key, self.window)
            results = await pipe.execute()

        count = results[1]
        if count >= self.limit:
            return False, 0
        return True, self.limit - count