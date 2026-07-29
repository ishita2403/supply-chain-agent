# tests/test_understanding_engine.py

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from supply_chain_agent.understanding.classifier import classify_event
from supply_chain_agent.models import SessionLocal
from supply_chain_agent.understanding.entity_linker import link_entities


def test_classifier_detects_supplier_delay():
    result = classify_event("Acme Electronics reports a 10-day delay on shipment due to a factory fire.")
    assert result.event_type == "supplier_delay"
    assert result.severity == "high"  # because "fire" is present


def test_classifier_detects_quality_issue():
    result = classify_event("Quality inspection flagged a 4% defect rate on Li-ion Battery batch #4521.")
    assert result.event_type == "quality_issue"


def test_classifier_unknown_when_no_keywords_match():
    result = classify_event("The weather today is sunny with a light breeze.")
    assert result.event_type == "unknown"
    assert result.event_type_confidence == 0.0


def test_entity_linker_finds_supplier():
    session = SessionLocal()
    links = link_entities(session, "Acme Electronics reports a delay.")
    assert links.supplier_id is not None
    assert links.supplier_match_score >= 75
    session.close()