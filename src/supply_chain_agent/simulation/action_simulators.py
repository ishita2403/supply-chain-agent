# src/supply_chain_agent/simulation/action_simulators.py

from ..impact.impact_report import ImpactReport
from .simulation_result import SimulationResult


def simulate_switch_supplier(action_details: dict, report: ImpactReport, plan_id: str) -> SimulationResult:
    quantity = action_details["quantity"]
    new_unit_cost = action_details["new_unit_cost"]
    new_lead_time = action_details["new_lead_time_days"]

    cost = quantity * new_unit_cost
    delay_reduction = max(0, report.source_delay_days - new_lead_time)
    # Revenue recovered scales with how much of the original delay this closes.
    recovery_fraction = min(1.0, delay_reduction / report.source_delay_days) if report.source_delay_days else 1.0
    revenue_recovered = report.total_revenue_at_risk * recovery_fraction

    # Risk: alternate suppliers are inherently less proven for this component
    # than the primary supplier -- approximate with a fixed uncertainty premium.
    NEW_SUPPLIER_RISK_PREMIUM = 15
    risk_score = 20 + NEW_SUPPLIER_RISK_PREMIUM

    return SimulationResult(
        plan_id=plan_id, strategy_type="alternate_supplier",
        cost=cost, delay_reduction_days=delay_reduction,
        customer_satisfaction_score=50 + recovery_fraction * 40,
        revenue_recovered=revenue_recovered,
        risk_score=risk_score,
        supplier_reliability_score=0.75,  # unproven-alternate assumption; refined below via DB lookup in orchestrator
    )


def simulate_expedite_shipping(action_details: dict, report: ImpactReport, plan_id: str) -> SimulationResult:
    quantity = action_details["quantity"]
    delay_recovered = action_details["delay_recovered_days"]
    cost_multiplier = action_details["cost_multiplier"]

    # Baseline shipping cost approximation: assume normal shipping is
    # roughly embedded in unit price already, so we model AIR FREIGHT
    # as an explicit PREMIUM on top, proportional to quantity.
    BASE_SHIPPING_COST_PER_UNIT = 1.0  # explicit domain assumption
    cost = quantity * BASE_SHIPPING_COST_PER_UNIT * cost_multiplier

    recovery_fraction = min(1.0, delay_recovered / report.source_delay_days) if report.source_delay_days else 1.0
    revenue_recovered = report.total_revenue_at_risk * recovery_fraction

    return SimulationResult(
        plan_id=plan_id, strategy_type="air_freight",
        cost=cost, delay_reduction_days=delay_recovered,
        customer_satisfaction_score=50 + recovery_fraction * 45,  # fast fix -> high satisfaction
        revenue_recovered=revenue_recovered,
        risk_score=25,  # logistics/capacity availability risk
        supplier_reliability_score=0.9,  # doesn't change supplier, just shipping method
    )


def simulate_reschedule_due_dates(action_details: dict, report: ImpactReport, plan_id: str) -> SimulationResult:
    # No delay is actually recovered -- we're just formally acknowledging it.
    return SimulationResult(
        plan_id=plan_id, strategy_type="reschedule_production",
        cost=0.0,  # no direct financial cost, only goodwill cost (captured via satisfaction)
        delay_reduction_days=0.0,
        customer_satisfaction_score=35,  # customers unhappy but informed, not blindsided
        revenue_recovered=0.0,
        risk_score=5,  # lowest-risk option -- nothing new can go wrong
        supplier_reliability_score=0.9,  # unchanged
    )


def simulate_allocate_inventory(action_details: dict, report: ImpactReport, plan_id: str) -> SimulationResult:
    units_covered = action_details["units_covered"]
    total_needed = sum(po.quantity for po in report.affected_pos) or 1

    coverage_fraction = min(1.0, units_covered / total_needed)
    revenue_recovered = report.total_revenue_at_risk * coverage_fraction
    # Inventory allocation doesn't fix the ROOT delay, but immediately
    # satisfies covered demand -- so satisfaction rises with coverage
    # even though delay_reduction_days stays at 0 (the underlying
    # disruption still needs a separate fix for uncovered demand).
    return SimulationResult(
        plan_id=plan_id, strategy_type="allocate_inventory",
        cost=0.0,  # using existing stock -- opportunity cost, not direct cash cost
        delay_reduction_days=0.0,
        inventory_used=units_covered,
        customer_satisfaction_score=40 + coverage_fraction * 40,
        revenue_recovered=revenue_recovered,
        risk_score=10,  # low risk -- using stock you already own
        supplier_reliability_score=0.9,
    )


def simulate_split_production(action_details: dict, report: ImpactReport, plan_id: str) -> SimulationResult:
    factory_split = action_details["factory_split"]
    quantity = action_details["quantity"]

    # Parallelizing production across N factories roughly divides the
    # remaining catch-up time by the number of factories involved
    # (a simplifying assumption -- real gains depend on each factory's
    # actual spare capacity, which we don't model at this fidelity).
    num_factories = len(factory_split)
    delay_reduction = report.source_delay_days * (1 - 1 / num_factories) if num_factories > 1 else 0

    recovery_fraction = min(1.0, delay_reduction / report.source_delay_days) if report.source_delay_days else 0
    revenue_recovered = report.total_revenue_at_risk * recovery_fraction

    # Utilization: splitting spreads load thinner per factory -- model as
    # each factory now running at its proportional share, which we treat
    # as "healthy" utilization (not overloaded) rather than a literal %.
    factory_utilization = 100 / num_factories * num_factories  # stays representationally 100 (evenly distributed)

    return SimulationResult(
        plan_id=plan_id, strategy_type="split_production",
        cost=quantity * 0.5,  # coordination/changeover overhead, explicit assumption
        delay_reduction_days=delay_reduction,
        customer_satisfaction_score=50 + recovery_fraction * 35,
        factory_utilization_pct=factory_utilization,
        revenue_recovered=revenue_recovered,
        risk_score=20,  # coordination complexity across factories
        supplier_reliability_score=0.9,
    )


def simulate_deprioritize_orders(action_details: dict, report: ImpactReport, plan_id: str) -> SimulationResult:
    protected_ids = set(action_details["protected_po_ids"])
    protected_revenue = sum(
        po.revenue_at_risk for po in report.affected_pos if po.po_id in protected_ids
    )
    # High-priority customers are fully protected -> their revenue is recovered;
    # low-priority ones still absorb the delay -> their revenue stays at risk.
    return SimulationResult(
        plan_id=plan_id, strategy_type="delay_low_priority",
        cost=0.0,
        delay_reduction_days=0.0,  # total delay isn't reduced, just REDISTRIBUTED
        customer_satisfaction_score=55,  # protects key accounts, upsets smaller ones -- net mixed
        revenue_recovered=protected_revenue,
        risk_score=15,  # relationship/reputational risk with deprioritized customers
        supplier_reliability_score=0.9,
    )


ACTION_SIMULATORS = {
    "switch_supplier": simulate_switch_supplier,
    "expedite_shipping": simulate_expedite_shipping,
    "reschedule_due_dates": simulate_reschedule_due_dates,
    "allocate_inventory": simulate_allocate_inventory,
    "split_production": simulate_split_production,
    "deprioritize_orders": simulate_deprioritize_orders,
}
