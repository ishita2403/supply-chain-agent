# tests/test_decision_scorer.py

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
from supply_chain_agent.scoring.scoring_weights import ScoringWeights
from supply_chain_agent.scoring.normalizer import normalize_metric
from supply_chain_agent.scoring.decision_scorer import score_all_plans
from supply_chain_agent.simulation.simulation_result import SimulationResult


def test_weights_must_sum_to_one():
    with pytest.raises(ValueError):
        ScoringWeights(cost=0.5, delay_reduction=0.5, customer_satisfaction=0.5,
                        risk=0.5, revenue_recovered=0.5, supplier_reliability=0.5)


def test_normalize_metric_handles_no_variation():
    result = normalize_metric({"a": 10, "b": 10, "c": 10}, higher_is_better=True)
    assert all(v == 0.5 for v in result.values())


def test_normalize_metric_inverts_for_lower_is_better():
    result = normalize_metric({"cheap": 100, "expensive": 500}, higher_is_better=False)
    assert result["cheap"] == 1.0
    assert result["expensive"] == 0.0


def test_scoring_ranks_plans_and_excludes_baseline():
    results = {
        "baseline_do_nothing": SimulationResult(plan_id="baseline_do_nothing", strategy_type="baseline"),
        "plan_a": SimulationResult(plan_id="plan_a", strategy_type="air_freight",
                                     cost=100, delay_reduction_days=8, customer_satisfaction_score=90,
                                     risk_score=20, revenue_recovered=50000, supplier_reliability_score=0.9),
        "plan_b": SimulationResult(plan_id="plan_b", strategy_type="reschedule_production",
                                     cost=0, delay_reduction_days=0, customer_satisfaction_score=35,
                                     risk_score=5, revenue_recovered=0, supplier_reliability_score=0.9),
    }
    scored = score_all_plans(results, ScoringWeights())
    assert len(scored) == 2  # baseline excluded
    assert scored[0].plan_id == "plan_a"  # clearly the stronger plan here


def test_score_breakdown_sums_to_overall_score():
    results = {
        "plan_a": SimulationResult(plan_id="plan_a", strategy_type="air_freight",
                                     cost=100, delay_reduction_days=8, customer_satisfaction_score=90,
                                     risk_score=20, revenue_recovered=50000, supplier_reliability_score=0.9),
        "plan_b": SimulationResult(plan_id="plan_b", strategy_type="reschedule_production",
                                     cost=0, delay_reduction_days=0, customer_satisfaction_score=35,
                                     risk_score=5, revenue_recovered=0, supplier_reliability_score=0.9),
    }
    scored = score_all_plans(results, ScoringWeights())
    for sp in scored:
        contributions_sum = sum(c.contribution for c in sp.score_breakdown.values())
        assert abs(contributions_sum - sp.overall_score) < 1e-9