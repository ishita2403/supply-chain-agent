# tests/test_recommender.py

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from supply_chain_agent.scoring.scored_plan import ScoredPlan
from supply_chain_agent.simulation.simulation_result import SimulationResult
from supply_chain_agent.recommendation.confidence import compute_margin_confidence
from supply_chain_agent.recommendation.guardrails import cost_ceiling_guardrail, low_confidence_guardrail
from supply_chain_agent.recommendation.recommender import recommend
from supply_chain_agent.models import Event


def test_margin_confidence_high_for_decisive_win():
    plans = [
        ScoredPlan(plan_id="a", strategy_type="air_freight", overall_score=0.81),
        ScoredPlan(plan_id="b", strategy_type="hybrid", overall_score=0.42),
    ]
    assert compute_margin_confidence(plans) == 1.0  # gap 0.39 > 0.3 threshold, capped at 1.0


def test_margin_confidence_low_for_near_tie():
    plans = [
        ScoredPlan(plan_id="a", strategy_type="air_freight", overall_score=0.63),
        ScoredPlan(plan_id="b", strategy_type="hybrid", overall_score=0.61),
    ]
    conf = compute_margin_confidence(plans)
    assert conf < 0.2  # gap of 0.02 is nearly no confidence signal


def test_margin_confidence_max_with_single_plan():
    plans = [ScoredPlan(plan_id="a", strategy_type="reschedule_production", overall_score=0.5)]
    assert compute_margin_confidence(plans) == 1.0


def test_cost_ceiling_guardrail_fires_above_threshold():
    result = SimulationResult(plan_id="a", strategy_type="air_freight", cost=30000)
    flag = cost_ceiling_guardrail(result, overall_confidence=0.9)
    assert flag is not None
    assert flag.forces_human_review is True


def test_cost_ceiling_guardrail_silent_below_threshold():
    result = SimulationResult(plan_id="a", strategy_type="air_freight", cost=5000)
    flag = cost_ceiling_guardrail(result, overall_confidence=0.9)
    assert flag is None


def test_recommend_flags_human_review_on_low_confidence():
    event = Event(id=1, confidence_score=0.1, raw_text="ambiguous event")
    scored = [
        ScoredPlan(plan_id="a", strategy_type="reschedule_production", overall_score=0.5),
        ScoredPlan(plan_id="b", strategy_type="air_freight", overall_score=0.48),
    ]
    sim_results = {
        "a": SimulationResult(plan_id="a", strategy_type="reschedule_production", cost=0),
        "b": SimulationResult(plan_id="b", strategy_type="air_freight", cost=1000),
    }
    rec = recommend(event, scored, sim_results)
    assert rec.decision_status == "requires_human_review"
    assert any(f.guardrail_name == "low_confidence" for f in rec.guardrail_flags)