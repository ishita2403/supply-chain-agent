# src/supply_chain_agent/ingestion/event_ingestion.py

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from ..models import Event
from .schemas import EventCreate


def ingest_event(session: Session, payload: EventCreate) -> Event:
    """
    Persists a single raw event. Idempotent with respect to
    external_reference_id: if an event with the same reference already
    exists, return the existing one instead of creating a duplicate.
    """
    if payload.external_reference_id:
        existing = (
            session.query(Event)
            .filter_by(external_reference_id=payload.external_reference_id)
            .first()
        )
        if existing:
            existing.source = payload.source
            existing.raw_text = payload.raw_text
            existing.reported_at = payload.reported_at
            existing.status = "raw"
            existing.event_type = None
            existing.severity = None
            existing.supplier_id = None
            existing.component_id = None
            existing.factory_id = None
            existing.confidence_score = None
            existing.understanding_notes = None
            session.add(existing)
            try:
                session.commit()
            except IntegrityError:
                session.rollback()
            session.refresh(existing)
            return existing

    event = Event(
        source=payload.source,
        raw_text=payload.raw_text,
        reported_at=payload.reported_at,
        external_reference_id=payload.external_reference_id,
        status="raw",
    )
    session.add(event)
    try:
        session.commit()
    except IntegrityError:
        # Race condition safety net: two near-simultaneous requests with the
        # same external_reference_id could both pass the check above before
        # either commits. The unique constraint on the column catches this;
        # we roll back and return the row the other request just inserted.
        session.rollback()
        existing = (
            session.query(Event)
            .filter_by(external_reference_id=payload.external_reference_id)
            .first()
        )
        return existing

    session.refresh(event)
    return event


def ingest_from_csv(session: Session, csv_path: str) -> list[Event]:
    """
    Simulates a batch 'pull' ingestion from an external system —
    e.g. a daily export from an ERP system.
    Expected CSV columns: source, raw_text, reported_at, external_reference_id
    """
    import csv
    from datetime import datetime

    ingested = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            reported_at = (
                datetime.fromisoformat(row["reported_at"])
                if row.get("reported_at")
                else None
            )
            payload = EventCreate(
                source=row["source"],
                raw_text=row["raw_text"],
                reported_at=reported_at,
                external_reference_id=row.get("external_reference_id") or None,
            )
            ingested.append(ingest_event(session, payload))
    return ingested