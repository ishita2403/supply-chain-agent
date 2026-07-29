# tests/test_plan_generator.py

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from supply_chain_agent.models import SessionLocal
from supply_chain_agent.ingestion.schemas import EventCreate
from supply_chain_agent.ingestion.event_ingestion import ingest_event
from supply_chain_agent.understanding.understanding_engine import understand_event
from supply_chain_agent.impact.impact_analysis import analyze_impact
from supply_chain_agent.recovery.plan_generator import generate_recovery_plans


def _build_understood_delay_event(session):
    payload = EventCreate(
        source="manual",
        raw_text="Acme Electronics reports a 10-day delay on Microcontroller Chip shipment due to a factory fire.",
    )
    event = ingest_event(session, payload)
    return understand_event(session, event)


def test_reschedule_plan_always_present():
    session = SessionLocal()
    event = _build_understood_delay_event(session)
    report = analyze_impact(session, event)
    plans = generate_recovery_plans(session, event, report)
    assert any(p.strategy_type == "reschedule_production" for p in plans)
    session.close()


def test_alternate_supplier_plan_generated_when_alternate_exists():
    session = SessionLocal()
    event = _build_understood_delay_event(session)
    report = analyze_impact(session, event)
    plans = generate_recovery_plans(session, event, report)
    assert any(p.strategy_type == "alternate_supplier" for p in plans)
    session.close()


def test_no_zero_plan_scenario():
    """Even a barely-understood event should never yield zero plans, thanks to reschedule."""
    session = SessionLocal()
    event = _build_understood_delay_event(session)
    report = analyze_impact(session, event)
    plans = generate_recovery_plans(session, event, report)
    assert len(plans) >= 1
    session.close()


def test_plan_actions_are_structured_and_non_empty():
    session = SessionLocal()
    event = _build_understood_delay_event(session)
    report = analyze_impact(session, event)
    plans = generate_recovery_plans(session, event, report)
    for p in plans:
        assert len(p.actions) > 0
        for action in p.actions:
            assert action.action_type
            assert isinstance(action.details, dict)
    session.close()