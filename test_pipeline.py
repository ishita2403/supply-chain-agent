import sys
sys.path.append("src")

from supply_chain_agent.models import SessionLocal
from supply_chain_agent.ingestion.event_ingestion import ingest_from_csv
from supply_chain_agent.understanding.understanding_engine import process_all_raw_events
from supply_chain_agent.impact.impact_analysis import analyze_impact
from supply_chain_agent.recovery.plan_generator import generate_recovery_plans
from supply_chain_agent.simulation.scenario_simulator import simulate_all_plans
from supply_chain_agent.scoring.decision_scorer import score_all_plans
from supply_chain_agent.recommendation.recommender import recommend
from supply_chain_agent.prediction.state_projector import project_post_recommendation_state
from supply_chain_agent.prediction.prediction_explainer import (
    build_prediction_trace,
    generate_prediction_narrative,
)

session = SessionLocal()
ingest_from_csv(session, "data/sample_events.csv")
events = process_all_raw_events(session)

event = events[0]
report = analyze_impact(session, event)
plans = generate_recovery_plans(session, event, report)
results = simulate_all_plans(plans, report)
scored = score_all_plans(results)
rec = recommend(event, scored, results)

selected_plan = next(p for p in plans if p.plan_id == rec.selected_plan_id)
selected_result = results[rec.selected_plan_id]

state = project_post_recommendation_state(
    event.id, report, selected_plan, selected_result
)
trace = build_prediction_trace(report, state)
narrative, source = generate_prediction_narrative(trace)

print(
    f"BEFORE severity: {report.overall_severity} | "
    f"AFTER severity: {state.residual_severity}"
)
print(
    f"BEFORE revenue at risk: ${report.total_revenue_at_risk:,.2f} | "
    f"AFTER: ${state.residual_revenue_at_risk:,.2f}"
)
print()
print(f"Narrative ({source}):")
print(narrative)