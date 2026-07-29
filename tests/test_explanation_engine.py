# tests/test_explanation_engine.py

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from unittest.mock import patch
from supply_chain_agent.models import SessionLocal
from supply_chain_agent.ingestion.schemas import EventCreate
from supply_chain_agent.ingestion.event_ingestion import ingest_event
from supply_chain_agent.understanding.understanding_engine import understand_event
from supply_chain_agent.impact.impact_analysis import analyze_impact
from supply_chain_agent.recovery.plan_generator import generate_recovery_plans
from supply_chain_agent.simulation.scenario_simulator import simulate_all_plans
from supply_chain_agent.scoring.decision_scorer import score_all_plans
from supply_chain_agent.recommendation.recommender import recommend
from supply_chain_agent.reasoning.explanation_engine import generate_explanation
from supply_chain_agent.reasoning.template_explainer import generate_template_explanation


def _full_pipeline():
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
    return session, event, report, scored, rec


def test_explanation_falls_back_to_template_when_llm_unavailable():
    session, event, report, scored, rec = _full_pipeline()
    with patch("supply_chain_agent.reasoning.explanation_engine.call_ollama", return_value=None):
        explanation = generate_explanation(session, event, report, scored, rec)
    assert explanation.narrative_source == "template"
    assert rec.selected_strategy_type.replace("_", " ") in explanation.narrative.replace("_", " ")
    session.close()


def test_explanation_rejects_llm_output_that_ignores_selected_plan():
    session, event, report, scored, rec = _full_pipeline()
    fake_bad_output = "We suggest doing nothing at all, which is totally unrelated wording."
    with patch("supply_chain_agent.reasoning.explanation_engine.call_ollama", return_value=fake_bad_output):
        explanation = generate_explanation(session, event, report, scored, rec)
    assert explanation.narrative_source == "template"  # sanity check correctly rejected it
    session.close()


def test_explanation_accepts_valid_llm_output():
    session, event, report, scored, rec = _full_pipeline()
    fake_good_output = f"We recommend the {rec.selected_strategy_type.replace('_', ' ')} plan based on the analysis."
    with patch("supply_chain_agent.reasoning.explanation_engine.call_ollama", return_value=fake_good_output):
        explanation = generate_explanation(session, event, report, scored, rec)
    assert explanation.narrative_source == "llm"
    session.close()


def test_reasoning_trace_contains_key_facts():
    session, event, report, scored, rec = _full_pipeline()
    explanation = generate_template_explanation(report, rec)  # direct template test, no LLM involved
    assert rec.selected_strategy_type in explanation
    assert str(report.source_delay_days) in explanation
    session.close()