# src/supply_chain_agent/simulation/scenario_simulator.py

from sqlalchemy.orm import Session
from ..impact.impact_report import ImpactReport
from ..recovery.recovery_plan import RecoveryPlan
from .simulation_result import SimulationResult, combine_partial_results
from .action_simulators import ACTION_SIMULATORS


def simulate_baseline(report: ImpactReport) -> SimulationResult:
    """
    'Do nothing' scenario -- the full, unmitigated disruption plays out.
    Every other plan's simulation result is meant to be compared against this.
    """
    return SimulationResult(
        plan_id="baseline_do_nothing",
        strategy_type="baseline",
        cost=0.0,
        delay_reduction_days=0.0,
        customer_satisfaction_score=20,  # full delay hits customers with no mitigation
        revenue_recovered=0.0,           # nothing recovered -- full revenue stays at risk
        risk_score=40,                    # doing nothing about a known disruption is itself a risk
        supplier_reliability_score=0.9,
    )


def simulate_plan(plan: RecoveryPlan, report: ImpactReport) -> SimulationResult:
    partials = []
    for action in plan.actions:
        simulator_fn = ACTION_SIMULATORS.get(action.action_type)
        if simulator_fn is None:
            continue  # unknown action type -- skip rather than crash; log-worthy in production
        partials.append(simulator_fn(action.details, report, plan.plan_id))

    return combine_partial_results(plan.plan_id, plan.strategy_type, partials)


def simulate_all_plans(plans: list[RecoveryPlan], report: ImpactReport) -> dict[str, SimulationResult]:
    """
    Returns a dict keyed by plan_id (plus 'baseline_do_nothing') so Phase 8's
    scorer can look up any plan's result by ID and compare directly against
    the baseline.
    """
    results = {"baseline_do_nothing": simulate_baseline(report)}
    for plan in plans:
        results[plan.plan_id] = simulate_plan(plan, report)
    return results