# src/supply_chain_agent/api/routes/events.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ...models import SessionLocal, Event
from ...ingestion.schemas import EventCreate, EventOut
from ...ingestion.event_ingestion import ingest_event
from ...impact.impact_analysis import analyze_impact
from ...recovery.plan_generator import generate_recovery_plans
from ...simulation.scenario_simulator import simulate_all_plans
from ...simulation.scenario_simulator import simulate_all_plans
from ...scoring.decision_scorer import score_all_plans
from ...scoring.scoring_weights import ScoringWeights
from ...recommendation.recommender import recommend
from ...reasoning.explanation_engine import generate_explanation
from ...prediction.state_projector import project_post_recommendation_state
from ...prediction.prediction_explainer import build_prediction_trace, generate_prediction_narrative
from ...orchestrator.agent_orchestrator import SupplyChainAgent
from pydantic import BaseModel
from ...scoring.scoring_weights import ScoringWeights

router = APIRouter(prefix="/events", tags=["events"])


def get_db():
    """Provides a DB session per-request, and guarantees it's closed after."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/ingest", response_model=EventOut)
def ingest(payload: EventCreate, db: Session = Depends(get_db)):
    event = ingest_event(db, payload)
    return event

# src/supply_chain_agent/api/routes/events.py  (add this)

from ...understanding.understanding_engine import process_all_raw_events

@router.post("/process")
def process_raw_events(db: Session = Depends(get_db)):
    processed = process_all_raw_events(db)
    return {
        "processed_count": len(processed),
        "events": [
            {
                "id": e.id, "event_type": e.event_type, "severity": e.severity,
                "supplier_id": e.supplier_id, "component_id": e.component_id,
                "confidence_score": e.confidence_score,
            }
            for e in processed
        ],
    }
# src/supply_chain_agent/api/routes/events.py  (add this)



@router.get("/{event_id}/impact")
def get_event_impact(event_id: int, db: Session = Depends(get_db)):
    event = db.query(Event).get(event_id)
    if event is None:
        return {"error": "Event not found"}
    if event.status == "raw":
        return {"error": "Event has not been processed yet. Call /events/process first."}

    report = analyze_impact(db, event)
    if report is None:
        return {"error": "Could not determine impact -- event was not linked to a known entity."}
    return report.to_dict()

# src/supply_chain_agent/api/routes/events.py  (add this)
@router.get("/{event_id}/recovery-plans")
def get_recovery_plans(event_id: int, db: Session = Depends(get_db)):
    event = db.query(Event).get(event_id)
    if event is None:
        return {"error": "Event not found"}

    report = analyze_impact(db, event)
    if report is None:
        return {"error": "Could not determine impact -- run /impact analysis first."}

    plans = generate_recovery_plans(db, event, report)
    return {"event_id": event_id, "plan_count": len(plans), "plans": [p.to_dict() for p in plans]}

# src/supply_chain_agent/api/routes/events.py  (add this)



@router.get("/{event_id}/simulate")
def simulate_event_plans(event_id: int, db: Session = Depends(get_db)):
    event = db.query(Event).get(event_id)
    if event is None:
        return {"error": "Event not found"}

    report = analyze_impact(db, event)
    if report is None:
        return {"error": "Could not determine impact."}

    plans = generate_recovery_plans(db, event, report)
    results = simulate_all_plans(plans, report)

    return {
        "event_id": event_id,
        "simulations": {pid: r.to_dict() for pid, r in results.items()},
    }
# src/supply_chain_agent/api/routes/events.py  (add this)



@router.get("/{event_id}/simulate")
def simulate_event_plans(event_id: int, db: Session = Depends(get_db)):
    event = db.query(Event).get(event_id)
    if event is None:
        return {"error": "Event not found"}

    report = analyze_impact(db, event)
    if report is None:
        return {"error": "Could not determine impact."}

    plans = generate_recovery_plans(db, event, report)
    results = simulate_all_plans(plans, report)

    return {
        "event_id": event_id,
        "simulations": {pid: r.to_dict() for pid, r in results.items()},
    }
# src/supply_chain_agent/api/routes/events.py  (add this)



@router.get("/{event_id}/score")
def score_event_plans(event_id: int, db: Session = Depends(get_db)):
    event = db.query(Event).get(event_id)
    if event is None:
        return {"error": "Event not found"}

    report = analyze_impact(db, event)
    if report is None:
        return {"error": "Could not determine impact."}

    plans = generate_recovery_plans(db, event, report)
    sim_results = simulate_all_plans(plans, report)
    scored = score_all_plans(sim_results, ScoringWeights())

    return {"event_id": event_id, "ranked_plans": [sp.to_dict() for sp in scored]}

# src/supply_chain_agent/api/routes/events.py  (add this)



@router.get("/{event_id}/recommend")
def recommend_for_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(Event).get(event_id)
    if event is None:
        return {"error": "Event not found"}

    report = analyze_impact(db, event)
    if report is None:
        return {"error": "Could not determine impact."}

    plans = generate_recovery_plans(db, event, report)
    sim_results = simulate_all_plans(plans, report)
    scored = score_all_plans(sim_results, ScoringWeights())

    recommendation = recommend(event, scored, sim_results)
    if recommendation is None:
        return {"error": "No plans available to recommend."}

    return recommendation.to_dict()

# src/supply_chain_agent/api/routes/events.py  (add this)


@router.get("/{event_id}/explain")
def explain_event_decision(event_id: int, db: Session = Depends(get_db)):
    event = db.query(Event).get(event_id)
    if event is None:
        return {"error": "Event not found"}

    report = analyze_impact(db, event)
    if report is None:
        return {"error": "Could not determine impact."}

    plans = generate_recovery_plans(db, event, report)
    sim_results = simulate_all_plans(plans, report)
    scored = score_all_plans(sim_results, ScoringWeights())
    recommendation = recommend(event, scored, sim_results)

    if recommendation is None:
        return {"error": "No recommendation available."}

    explanation = generate_explanation(db, event, report, scored, recommendation)

    return {
        "event_id": event_id,
        "reasoning_trace": explanation.reasoning_trace,
        "narrative": explanation.narrative,
        "narrative_source": explanation.narrative_source,
    }

# src/supply_chain_agent/api/routes/events.py  (add this)



@router.get("/{event_id}/predict")
def predict_post_recommendation_state(event_id: int, db: Session = Depends(get_db)):
    event = db.query(Event).get(event_id)
    if event is None:
        return {"error": "Event not found"}

    report = analyze_impact(db, event)
    if report is None:
        return {"error": "Could not determine impact."}

    plans = generate_recovery_plans(db, event, report)
    sim_results = simulate_all_plans(plans, report)
    scored = score_all_plans(sim_results, ScoringWeights())
    recommendation = recommend(event, scored, sim_results)
    if recommendation is None:
        return {"error": "No recommendation available."}

    selected_plan = next(p for p in plans if p.plan_id == recommendation.selected_plan_id)
    selected_sim_result = sim_results[recommendation.selected_plan_id]

    state = project_post_recommendation_state(event_id, report, selected_plan, selected_sim_result)
    trace = build_prediction_trace(report, state)
    narrative, source = generate_prediction_narrative(trace)
    state.narrative = narrative
    state.narrative_source = source

    return state.to_dict()

@router.get("/{event_id}/full-analysis")
def run_full_agent_analysis(event_id: int, db: Session = Depends(get_db)):
    agent = SupplyChainAgent(db)
    run = agent.process_event(event_id)
    return run.to_dict()

# src/supply_chain_agent/api/routes/events.py  (add this)



class WeightsInput(BaseModel):
    cost: float = 0.20
    delay_reduction: float = 0.25
    customer_satisfaction: float = 0.20
    risk: float = 0.15
    revenue_recovered: float = 0.15
    supplier_reliability: float = 0.05

@router.post("/{event_id}/run")
def run_agent_with_weights(event_id: int, weights: WeightsInput, db: Session = Depends(get_db)):
    scoring_weights = ScoringWeights(**weights.model_dump())
    agent = SupplyChainAgent(db, scoring_weights=scoring_weights)
    run = agent.process_event(event_id)
    return run.to_dict()