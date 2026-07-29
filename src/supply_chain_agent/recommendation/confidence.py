# src/supply_chain_agent/recommendation/confidence.py

from ..scoring.scored_plan import ScoredPlan


def compute_margin_confidence(scored_plans: list[ScoredPlan]) -> float:
    """
    Measures how decisive the top choice is, based on the score gap between
    #1 and #2. Returns a 0-1 confidence value.

    - If there's only one plan, there's no alternative to be uncertain
      against, so confidence is maximal (1.0).
    - A large gap (e.g. 0.81 vs 0.42 -> gap 0.39) means a clear winner -> high confidence.
    - A tiny gap (e.g. 0.63 vs 0.61 -> gap 0.02) means a near-tie -> low confidence.
    """
    if len(scored_plans) <= 1:
        return 1.0

    top_score = scored_plans[0].overall_score
    runner_up_score = scored_plans[1].overall_score
    gap = top_score - runner_up_score

    # A gap of 0.3+ (out of a max possible 1.0) is treated as fully decisive;
    # scale linearly below that. This threshold is an explicit, statable
    # design choice, not a derived constant.
    DECISIVE_GAP_THRESHOLD = 0.3
    return min(1.0, gap / DECISIVE_GAP_THRESHOLD)


def compute_overall_confidence(event_confidence: float, margin_confidence: float) -> float:
    """
    Combines two INDEPENDENT sources of uncertainty:
      - event_confidence: how well was the disruption itself understood? (Phase 3)
      - margin_confidence: how clear-cut was the choice among plans? (Phase 8's margin)

    We weight event_confidence slightly higher, because a shaky
    understanding of the underlying event undermines EVERYTHING built on
    top of it, whereas a close scoring margin just means two options were
    both reasonably good -- a softer form of uncertainty.
    """
    return round(0.6 * event_confidence + 0.4 * margin_confidence, 3)


def confidence_label(overall_confidence: float) -> str:
    if overall_confidence >= 0.75:
        return "high"
    if overall_confidence >= 0.45:
        return "medium"
    return "low"