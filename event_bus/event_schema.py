"""
AFM Event Schema — Pydantic v2 validation
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class EventType(str, Enum):
    PAYMENT_INITIATED = "payment.initiated"
    PAYMENT_COMPLETED = "payment.completed"
    PAYMENT_FAILED = "payment.failed"
    TRADE_EXECUTED = "trade.executed"
    TRADE_FAILED = "trade.failed"
    SETTLEMENT_BATCH_CREATED = "settlement.batch_created"
    SETTLEMENT_BATCH_COMPLETED = "settlement.batch_completed"


class EventMetadata(BaseModel):
    event_id: str = Field(default_factory=lambda: f"evt_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    source: str = "afm"
    version: str = "1.0"


class BaseEvent(BaseModel):
    metadata: EventMetadata = Field(default_factory=EventMetadata)
    event_type: EventType
    payload: dict
