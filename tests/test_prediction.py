# tests/test_prediction.py

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from supply_chain_agent.models import SessionLocal
from supply_chain_agent.ingestion.schemas import EventCreate
from supply_chain_agent.ingestion.event_ingestion import ingest_event
from supply_chain_agent.understanding.understanding_engine import understand_event
from supply_chain_agent.impact.impact_analysis import analyze_impact
from supply_chain_agent.recovery.plan_generator import generate_recovery_plans
from supply_chain_agent.simulation.scenario_simulator import simulate_all_plans
from supply_chain_agent.scoring.decision_scorer import score_all_plans
from supply_chain_agent.recommendation.recommender import recommend
from supply_chain_agent.prediction.state_projector import project_post_recommendation_state


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
    results = simulate_all_plans(plans, report)
    scored = score_all_plans(results)
    rec = recommend(event, scored, results)
    selected_plan = next(p for p in plans if p.plan_id == rec.selected_plan_id)
    return report, selected_plan, results[rec.selected_plan_id], event.id


def test_residual_revenue_never_exceeds_original():
    report, plan, sim_result, event_id = _setup()
    state = project_post_recommendation_state(event_id, report, plan, sim_result)
    assert state.residual_revenue_at_risk <= report.total_revenue_at_risk + 0.01


def test_projected_delay_never_negative():
    report, plan, sim_result, event_id = _setup()
    state = project_post_recommendation_state(event_id, report, plan, sim_result)
    assert all(p.projected_delay_days >= 0 for p in state.projected_pos)


def test_severity_uses_same_scale_as_impact_report():
    report, plan, sim_result, event_id = _setup()
    state = project_post_recommendation_state(event_id, report, plan, sim_result)
    assert state.residual_severity in ("low", "medium", "high", "critical")
    assert report.overall_severity in ("low", "medium", "high", "critical")


def test_reschedule_plan_does_not_reduce_delay():
    """Sanity check: a plan that reduces zero delay should leave POs still at risk."""
    report, plan, sim_result, event_id = _setup()
    if plan.strategy_type == "reschedule_production":
        state = project_post_recommendation_state(event_id, report, plan, sim_result)
        assert all(p.still_at_risk for p in state.projected_pos)