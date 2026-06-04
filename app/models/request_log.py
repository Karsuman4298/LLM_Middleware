# app/models/request_log.py
from sqlalchemy import Column, String, Integer, Float, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base

class RequestLog(Base):
    __tablename__ = "request_logs"

    id          = Column(Integer, primary_key=True, index=True)
    api_key     = Column(String, index=True)
    model       = Column(String, index=True)
    provider    = Column(String)
    prompt_hash = Column(String)
    input_tokens  = Column(Integer)
    output_tokens = Column(Integer)
    latency_ms  = Column(Float)
    cost_usd    = Column(Float, default=0.0)  # free tier = 0
    status      = Column(String)
    error       = Column(Text, nullable=True)
    created_at  = Column(DateTime, server_default=func.now(), index=True)
    