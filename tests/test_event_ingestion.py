# tests/test_event_ingestion.py

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from supply_chain_agent.models import SessionLocal, Base, engine, Event
from supply_chain_agent.ingestion.schemas import EventCreate
from supply_chain_agent.ingestion.event_ingestion import ingest_event, ingest_from_csv


def setup_module():
    Base.metadata.create_all(bind=engine)


def test_ingest_creates_raw_event():
    session = SessionLocal()
    payload = EventCreate(source="manual", raw_text="Test delay event for unit test.")
    event = ingest_event(session, payload)
    assert event.id is not None
    assert event.status == "raw"
    session.close()


def test_ingest_is_idempotent():
    session = SessionLocal()
    payload = EventCreate(
        source="manual", raw_text="Duplicate test event",
        external_reference_id="DUPLICATE-CHECK-001",
    )
    first = ingest_event(session, payload)
    second = ingest_event(session, payload)
    assert first.id == second.id
    session.close()


def test_reingest_resets_existing_event_for_reprocessing():
    session = SessionLocal()
    payload = EventCreate(
        source="manual",
        raw_text="Re-ingest test event",
        external_reference_id="REPROCESS-001",
    )
    event = ingest_event(session, payload)
    event.status = "understood"
    event.event_type = "supplier_delay"
    event.severity = "high"
    event.confidence_score = 0.95
    event.understanding_notes = "Already understood"
    session.commit()

    reingested = ingest_event(session, payload)

    assert reingested.id == event.id
    assert reingested.status == "raw"
    assert reingested.event_type is None
    assert reingested.confidence_score is None
    session.close()


def test_batch_csv_ingestion():
    session = SessionLocal()
    csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "sample_events.csv")
    events = ingest_from_csv(session, csv_path)
    assert len(events) == 3
    assert all(e.status == "raw" for e in events)
    session.close()