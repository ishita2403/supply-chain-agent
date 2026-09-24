from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from ..models import Event
from .schemas import EventCreate


def ingest_event(session: Session, payload: EventCreate) -> Event:
    """
    Persists a single raw event.

    If an event with the same external_reference_id already exists,
    return the existing event without resetting its understanding.
    """

    if payload.external_reference_id:
        existing = (
            session.query(Event)
            .filter_by(external_reference_id=payload.external_reference_id)
            .first()
        )

        if existing:
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
        session.rollback()

        existing = (
            session.query(Event)
            .filter_by(external_reference_id=payload.external_reference_id)
            .first()
        )

        if existing:
            return existing

        raise

    session.refresh(event)
    return event


def ingest_from_csv(session: Session, csv_path: str) -> list[Event]:
    """
    Ingests events from a CSV file.

    Expected CSV columns:
    source, raw_text, reported_at, external_reference_id
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