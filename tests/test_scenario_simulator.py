# tests/test_scenario_simulator.py

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from supply_chain_agent.models import SessionLocal
from supply_chain_agent.ingestion.schemas import EventCreate
from supply_chain_agent.ingestion.event_ingestion import ingest_event
from supply_chain_agent.understanding.understanding_engine import understand_event
from supply_chain_agent.impact.impact_analysis import analyze_impact
from supply_chain_agent.recovery.plan_generator import generate_recovery_plans
from supply_chain_agent.simulation.scenario_simulator import simulate_all_plans, simulate_baseline


def _setup():
    session = SessionLocal()
    payload = EventCreate(
        source="manual",
        raw_text="Acme Electronics reports a 10-day delay on Microcontroller Chip shipment due to a factory fire.",
    )
    event = ingest_event(session, payload)
    event = understand_event(session, event)
    report = analyze_impact(session, event)
    plans = generate_recovery_plans(session, event, report)
    return session, plans, report


def test_baseline_has_zero_recovery():
    session, plans, report = _setup()
    baseline = simulate_baseline(report)
    assert baseline.revenue_recovered == 0.0
    assert baseline.delay_reduction_days == 0.0
    session.close()


def test_all_plans_produce_results():
    session, plans, report = _setup()
    results = simulate_all_plans(plans, report)
    assert "baseline_do_nothing" in results
    assert len(results) == len(plans) + 1
    session.close()


def test_air_freight_reduces_more_delay_than_reschedule():
    session, plans, report = _setup()
    results = simulate_all_plans(plans, report)
    air_freight = next((r for pid, r in results.items() if r.strategy_type == "air_freight"), None)
    reschedule = next((r for pid, r in results.items() if r.strategy_type == "reschedule_production"), None)
    assert air_freight is not None and reschedule is not None
    assert air_freight.delay_reduction_days > reschedule.delay_reduction_days


def test_no_plan_recovers_more_revenue_than_total_at_risk():
    session, plans, report = _setup()
    results = simulate_all_plans(plans, report)
    for r in results.values():
        assert r.revenue_recovered <= report.total_revenue_at_risk + 0.01  # float tolerance
    session.close()