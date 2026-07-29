# src/supply_chain_agent/understanding/understanding_engine.py

from sqlalchemy.orm import Session
from ..models import Event
from .classifier import classify_event
from .entity_linker import link_entities


def understand_event(session: Session, event: Event) -> Event:
    classification = classify_event(event.raw_text)
    links = link_entities(session, event.raw_text)

    event.event_type = classification.event_type
    event.severity = classification.severity
    event.supplier_id = links.supplier_id
    event.component_id = links.component_id
    event.factory_id = links.factory_id

    # Overall confidence combines classification confidence with how
    # well we were able to link to a specific entity. We weight
    # classification slightly higher, since "what kind of event" matters
    # more than "which exact entity" for downstream severity-based logic.
    entity_scores = [s for s in (
        links.supplier_match_score, links.component_match_score, links.factory_match_score
    ) if s > 0]
    avg_entity_confidence = (sum(entity_scores) / len(entity_scores) / 100) if entity_scores else 0.0

    event.confidence_score = round(
        0.6 * classification.event_type_confidence + 0.4 * avg_entity_confidence, 2
    )

    event.understanding_notes = (
        f"Matched keywords: {classification.matched_keywords}. "
        f"Supplier match score: {links.supplier_match_score:.0f}, "
        f"Component match score: {links.component_match_score:.0f}, "
        f"Factory match score: {links.factory_match_score:.0f}."
    )

    event.status = "understood"
    session.add(event)
    session.commit()
    session.refresh(event)
    return event


def process_all_raw_events(session: Session) -> list[Event]:
    """Convenience batch runner — picks up every unprocessed event."""
    raw_events = session.query(Event).filter_by(status="raw").all()
    return [understand_event(session, e) for e in raw_events]