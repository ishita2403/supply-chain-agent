# tests/scenarios/scenario_definitions.py

from dataclasses import dataclass
from typing import Callable

@dataclass
class Scenario:
    name: str
    raw_text: str
    description: str
    # Each expectation is a small, named callable taking the AgentRun and
    # returning (passed: bool, message: str) -- keeps assertions readable
    # and gives a clear failure message per expectation, not just a bare
    # AssertionError.
    expectations: list[Callable]


def _expect_status(status):
    def check(run):
        ok = run.status == status
        return ok, f"expected status={status}, got {run.status}"
    return check


def _expect_strategy_offered(strategy_type):
    def check(run):
        offered = {p.strategy_type for p in run.plans}
        ok = strategy_type in offered
        return ok, f"expected '{strategy_type}' to be offered; offered={offered}"
    return check


def _expect_strategy_not_offered(strategy_type):
    def check(run):
        offered = {p.strategy_type for p in run.plans}
        ok = strategy_type not in offered
        return ok, f"expected '{strategy_type}' NOT to be offered; offered={offered}"
    return check


def _expect_confidence_label(label):
    def check(run):
        ok = run.recommendation is not None and run.recommendation.confidence_label == label
        actual = run.recommendation.confidence_label if run.recommendation else None
        return ok, f"expected confidence_label={label}, got {actual}"
    return check


def _expect_decision_status(status):
    def check(run):
        ok = run.recommendation is not None and run.recommendation.decision_status == status
        actual = run.recommendation.decision_status if run.recommendation else None
        return ok, f"expected decision_status={status}, got {actual}"
    return check


def _expect_guardrail(name):
    def check(run):
        ok = run.recommendation is not None and any(
            f.guardrail_name == name for f in run.recommendation.guardrail_flags
        )
        return ok, f"expected guardrail '{name}' to fire"
    return check


SCENARIOS = [
    Scenario(
        name="clean_win",
        description="A clear, well-understood supplier delay with a strong alternate-supplier option.",
        raw_text="Acme Electronics reports a 10-day delay on Microcontroller Chip shipment due to a factory fire.",
        expectations=[_expect_status("complete"), _expect_strategy_offered("alternate_supplier")],
    ),
    Scenario(
        name="no_alternate_supplier",
        description="A disruption on a single-sourced component -- alternate_supplier must NOT be offered.",
        raw_text="Sole Source Casings Ltd reports a 12-day delay on Custom Casing shipment.",
        expectations=[_expect_status("complete"), _expect_strategy_not_offered("alternate_supplier")],
    ),
    Scenario(
        name="split_production_available",
        description="A disruption on a component used in a product made at two factories.",
        raw_text="Acme Electronics reports a 10-day delay on Microcontroller Chip shipment due to a factory fire.",
        expectations=[_expect_strategy_offered("split_production")],
    ),
    Scenario(
        name="cost_ceiling_triggers_review",
        description="A large-quantity order pushes the top plan's cost past the guardrail ceiling.",
        raw_text="Sole Source Casings Ltd reports a 15-day delay on Custom Casing shipment, factory shutdown.",
        expectations=[_expect_decision_status("requires_human_review"), _expect_guardrail("cost_ceiling")],
    ),
    Scenario(
        name="ambiguous_event_low_confidence",
        description="Vague, hard-to-classify text should propagate low confidence through to the recommendation.",
        raw_text="There was some kind of issue reported, details unclear at this time.",
        expectations=[_expect_status("incomplete")],  # entity linking will fail entirely -- correct hard stop
    ),
    Scenario(
        name="multi_tier_customers",
        description="A disruption affecting customers across multiple priority tiers.",
        raw_text="Acme Electronics reports a 10-day delay on Microcontroller Chip shipment due to a factory fire.",
        expectations=[_expect_strategy_offered("delay_low_priority")],
    ),
    Scenario(
        name="inventory_buffer_available",
        description="A disruption on a product with existing finished-goods inventory to draw on.",
        raw_text="Acme Electronics reports a 6-day delay on Microcontroller Chip shipment.",
        expectations=[_expect_strategy_offered("allocate_inventory")],
    ),
    Scenario(
        name="low_severity_minor_event",
        description="A minor, low-severity disruption -- system should not manufacture false urgency.",
        raw_text="Acme Electronics confirms a minor 1-day delay, largely resolved.",
        expectations=[_expect_status("complete")],
    ),
]
