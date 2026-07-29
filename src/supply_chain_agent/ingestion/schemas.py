# src/supply_chain_agent/ingestion/schemas.py

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class EventCreate(BaseModel):
    """What an external source sends us when reporting a disruption."""
    source: str = Field(..., description="Origin of this event, e.g. 'supplier_portal'")
    raw_text: str = Field(..., min_length=5, description="Free-text description of the disruption")
    reported_at: Optional[datetime] = None
    external_reference_id: Optional[str] = None


class EventOut(BaseModel):
    """What we return after ingesting an event."""
    id: int
    source: str
    raw_text: str
    status: str
    ingested_at: datetime

    class Config:
        from_attributes = True  # allows creating this from an SQLAlchemy object directly