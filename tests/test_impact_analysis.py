# tests/test_impact_analysis.py

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from supply_chain_agent.models import SessionLocal
from supply_chain_agent.ingestion.schemas import EventCreate
from supply_chain_agent.ingestion.event_ingestion import ingest_event
from supply_chain_agent.understanding.understanding_engine import understand_event
from supply_chain_agent.impact.impact_analysis import analyze_impact
from supply_chain_agent.impact.delay_estimator import estimate_source_delay_days


def test_delay_extraction_from_explicit_text():
    days, method = estimate_source_delay_days(
        "Acme Electronics reports a 10-day delay on shipment.", "supplier_delay", "high"
    )
    assert days == 10
    assert method == "extracted_from_text"


def test_delay_fallback_when_no_number_present():
    days, method = estimate_source_delay_days(
        "Supplier reports ongoing disruption of unclear length.", "supplier_delay", "medium"
    )
    assert days == 7
    assert method == "severity_based_default"


def test_full_pipeline_produces_impact_report():
    session = SessionLocal()
    payload = EventCreate(
        source="manual",
        raw_text="Acme Electronics reports a 10-day delay on Microcontroller Chip shipment due to a factory fire.",
    )
    event = ingest_event(session, payload)
    event = understand_event(session, event)
    report = analyze_impact(session, event)

    assert report is not None
    assert report.source_delay_days == 10
    assert "Smart Sensor Device" in report.affected_product_names
    assert len(report.affected_pos) >= 1
    assert report.total_revenue_at_risk > 0
    assert report.overall_severity in ("low", "medium", "high", "critical")
    session.close()