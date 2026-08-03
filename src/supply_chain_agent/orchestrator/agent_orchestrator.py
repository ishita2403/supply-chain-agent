# src/supply_chain_agent/orchestrator/agent_orchestrator.py

from sqlalchemy.orm import Session

from ..models import Event
from ..graph.dependency_graph import build_graph
from ..understanding.understanding_engine import understand_event
from ..impact.impact_analysis import analyze_impact
from ..recovery.plan_generator import generate_recovery_plans
from ..simulation.scenario_simulator import simulate_all_plans
from ..scoring.decision_scorer import score_all_plans
from ..scoring.scoring_weights import ScoringWeights
from ..recommendation.recommender import recommend
from ..reasoning.explanation_engine import generate_explanation
from ..prediction.state_projector import project_post_recommendation_state
from ..prediction.prediction_explainer import (
    build_prediction_trace,
    generate_prediction_narrative,
)
from .agent_run import AgentRun


class SupplyChainAgent:
    """
    The single, coherent entry point into the entire pipeline.
    Owns configuration (scoring weights) that persists across calls,
    and guarantees consistent, explicit handling of every failure point
    identified in Section 2.3.
    """

    def __init__(self, session: Session, scoring_weights: ScoringWeights | None = None):
        self.session = session
        self.scoring_weights = scoring_weights or ScoringWeights()

    def set_scoring_weights(self, weights: ScoringWeights) -> None:
        """Lets a caller change business priorities once, affecting all future runs."""
        self.scoring_weights = weights

    def process_event(self, event_id: int, skip_llm: bool = False) -> AgentRun:
        run = AgentRun(event_id=event_id)

        # ----------------------------------------------------
        # Step 1: Fetch event
        # ----------------------------------------------------
        event = self.session.query(Event).get(event_id)
        if event is None:
            return self._stop(
                run,
                "fetch_event",
                f"Event {event_id} not found."
            )
        run.event = event

        # ----------------------------------------------------
        # Step 2: Understand event
        # ----------------------------------------------------
        if event.status == "raw":
            event = understand_event(self.session, event)
            run.event = event

        # ----------------------------------------------------
        # Build dependency graph ONCE
        # ----------------------------------------------------
        graph = build_graph(self.session)

        # ----------------------------------------------------
        # Step 3: Impact Analysis
        # ----------------------------------------------------
        report = analyze_impact(
            self.session,
            event,
            graph=graph,
        )

        if report is None:
            return self._stop(
                run,
                "impact_analysis",
                "Could not determine impact -- event was not linked to a known "
                "supplier, component, or factory. Manual classification is required."
            )

        run.report = report

        # ----------------------------------------------------
        # Step 4: Recovery Plan Generation
        # ----------------------------------------------------
        plans = generate_recovery_plans(
            self.session,
            event,
            report,
        )

        if not plans:
            return self._stop(
                run,
                "recovery_plan_generation",
                "No recovery plans could be generated for this event "
                "(unexpected -- reschedule should always be feasible; "
                "check plan generator logic)."
            )

        run.plans = plans

        # ----------------------------------------------------
        # Step 5: Scenario Simulation
        # ----------------------------------------------------
        sim_results = simulate_all_plans(plans, report)
        run.sim_results = sim_results

        # ----------------------------------------------------
        # Step 6: Decision Scoring
        # ----------------------------------------------------
        scored_plans = score_all_plans(
            sim_results,
            self.scoring_weights,
        )

        run.scored_plans = scored_plans

        # ----------------------------------------------------
        # Step 7: Recommendation
        # ----------------------------------------------------
        recommendation = recommend(
            event,
            scored_plans,
            sim_results,
        )

        if recommendation is None:
            return self._stop(
                run,
                "recommendation",
                "No recommendation could be produced."
            )

        run.recommendation = recommendation

        # ----------------------------------------------------
        # Step 8: Explanation
        # ----------------------------------------------------
        explanation = generate_explanation(
            self.session,
            event,
            report,
            scored_plans,
            recommendation,
            graph=graph,
            skip_llm=skip_llm,
        )

        run.explanation = explanation

        # ----------------------------------------------------
        # Step 9: Prediction
        # ----------------------------------------------------
        selected_plan = next(
            p for p in plans
            if p.plan_id == recommendation.selected_plan_id
        )

        selected_sim_result = sim_results[
            recommendation.selected_plan_id
        ]

        post_state = project_post_recommendation_state(
            event_id,
            report,
            selected_plan,
            selected_sim_result,
        )

        trace = build_prediction_trace(report, post_state)

        if skip_llm:
            narrative = " ".join(trace)
            source = "template"
        else:
            narrative, source = generate_prediction_narrative(trace)

        post_state.narrative = narrative
        post_state.narrative_source = source

        run.post_state = post_state

        run.status = "complete"
        return run

    @staticmethod
    def _stop(run: AgentRun, step: str, reason: str) -> AgentRun:
        run.status = "incomplete"
        run.stopped_at_step = step
        run.stop_reason = reason
        return run