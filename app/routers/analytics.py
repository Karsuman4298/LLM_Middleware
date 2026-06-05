from fastapi import APIRouter
from sqlalchemy import select, func
from app.database import AsyncSession
from app.models.request_log import RequestLog

router = APIRouter()

@router.get("/analytics/usage")
async def usage():
    async with AsyncSession() as session:

        # total requests + tokens per model
        rows = await session.execute(
            select(
                RequestLog.model,
                RequestLog.status,
                func.count(RequestLog.id).label("total_requests"),
                func.sum(RequestLog.input_tokens).label("total_input_tokens"),
                func.sum(RequestLog.output_tokens).label("total_output_tokens"),
                func.avg(RequestLog.latency_ms).label("avg_latency_ms"),
            )
            .group_by(RequestLog.model, RequestLog.status)
            .order_by(func.count(RequestLog.id).desc())
        )
        results = rows.fetchall()

        # overall totals
        totals = await session.execute(
            select(
                func.count(RequestLog.id).label("total_requests"),
                func.sum(RequestLog.input_tokens).label("total_input_tokens"),
                func.sum(RequestLog.output_tokens).label("total_output_tokens"),
            )
            .where(RequestLog.status == "success")
        )
        t = totals.fetchone()

        return {
            "summary": {
                "total_requests":      t.total_requests or 0,
                "total_input_tokens":  t.total_input_tokens or 0,
                "total_output_tokens": t.total_output_tokens or 0,
                "total_cost_usd":      0.0,  # free tier
            },
            "by_model": [
                {
                    "model":              r.model,
                    "status":             r.status,
                    "requests":           r.total_requests,
                    "input_tokens":       r.total_input_tokens or 0,
                    "output_tokens":      r.total_output_tokens or 0,
                    "avg_latency_ms":     round(r.avg_latency_ms or 0, 2),
                }
                for r in results
            ]
        }

@router.get("/analytics/rate-limits")
async def rate_limits():
    async with AsyncSession() as session:
        rows = await session.execute(
            select(
                RequestLog.api_key,
                func.count(RequestLog.id).label("total_requests"),
                func.sum(RequestLog.input_tokens).label("total_tokens"),
            )
            .group_by(RequestLog.api_key)
            .order_by(func.count(RequestLog.id).desc())
        )
        results = rows.fetchall()
        return {
            "by_api_key": [
                {
                    "api_key":        r.api_key,
                    "total_requests": r.total_requests,
                    "total_tokens":   r.total_tokens or 0,
                }
                for r in results
            ]
        }
