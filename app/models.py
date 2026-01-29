# app/models.py
from enum import Enum as PyEnum
from datetime import datetime

from sqlalchemy import Column, String, Integer, Enum, func
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import DeclarativeBase


class CallStatus(str, PyEnum):
    """Possible states of a call in our system"""
    IN_PROGRESS    = "IN_PROGRESS"
    PROCESSING_AI  = "PROCESSING_AI"
    COMPLETED      = "COMPLETED"
    FAILED         = "FAILED"
    ARCHIVED       = "ARCHIVED"


class Base(DeclarativeBase):
    """Base class for all models"""
    pass


class Call(Base):
    __tablename__ = "calls"

    call_id        = Column(String, primary_key=True, index=True)
    status         = Column(Enum(CallStatus), default=CallStatus.IN_PROGRESS, nullable=False)
    last_sequence  = Column(Integer, default=0, nullable=False)          # highest sequence seen
    packet_count   = Column(Integer, default=0, nullable=False)
    transcription  = Column(String, nullable=True)
    sentiment      = Column(String, nullable=True)                       # e.g. "positive", "negative", "neutral"
    created_at     = Column(TIMESTAMP, server_default=func.now())
    updated_at     = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())