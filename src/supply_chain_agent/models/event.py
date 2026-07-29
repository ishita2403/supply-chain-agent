# src/supply_chain_agent/models/event.py

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Float,
)
from sqlalchemy.sql import func

from .base import Base


class Event(Base):
    __tablename__ = "events"

    # Primary Key
    id = Column(Integer, primary_key=True)

    # -------------------------
    # Ingestion Information
    # -------------------------
    source = Column(String, nullable=False)
    raw_text = Column(String, nullable=False)

    # Timestamp provided by the source system
    reported_at = Column(DateTime, nullable=True)

    # Timestamp when our system ingested the event
    ingested_at = Column(DateTime, server_default=func.now())

    # Prevent duplicate ingestion from external systems
    external_reference_id = Column(String, unique=True, nullable=True)

    # -------------------------
    # Event Understanding
    # -------------------------
    status = Column(String, nullable=False, default="raw")
    event_type = Column(String, nullable=True)
    severity = Column(String, nullable=True)

    # IDs determined by the understanding engine
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=True)
    component_id = Column(Integer, ForeignKey("components.id"), nullable=True)
    factory_id = Column(Integer, ForeignKey("factories.id"), nullable=True)

    # Confidence of the event classification (0.0–1.0)
    confidence_score = Column(Float, nullable=True)

    # Human-readable explanation of why the event was classified this way
    understanding_notes = Column(String, nullable=True)