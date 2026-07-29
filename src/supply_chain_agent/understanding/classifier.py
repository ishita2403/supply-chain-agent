# src/supply_chain_agent/understanding/classifier.py

from dataclasses import dataclass
from .keyword_rules import EVENT_TYPE_KEYWORDS, SEVERITY_KEYWORDS


@dataclass
class ClassificationResult:
    event_type: str
    event_type_score: float       # raw weighted score of the winning category
    event_type_confidence: float  # normalized 0-1
    severity: str
    matched_keywords: list[str]   # for the audit trail / understanding_notes


def classify_event(raw_text: str) -> ClassificationResult:
    text_lower = raw_text.lower()

    # --- Score every event_type category ---
    category_scores: dict[str, float] = {}
    category_matches: dict[str, list[str]] = {}

    for category, keyword_weights in EVENT_TYPE_KEYWORDS.items():
        score = 0.0
        matched = []
        for keyword, weight in keyword_weights:
            if keyword in text_lower:
                score += weight
                matched.append(keyword)
        if score > 0:
            category_scores[category] = score
            category_matches[category] = matched

    if not category_scores:
        # Nothing matched at all — flag as unknown rather than guessing.
        return ClassificationResult(
            event_type="unknown",
            event_type_score=0.0,
            event_type_confidence=0.0,
            severity="unknown",
            matched_keywords=[],
        )

    best_category = max(category_scores, key=category_scores.get)
    best_score = category_scores[best_category]

    # Normalize confidence: how dominant was the winning category vs
    # the sum of all category scores? (A clean win -> high confidence;
    # a near-tie between two categories -> lower confidence.)
    total_score = sum(category_scores.values())
    confidence = best_score / total_score if total_score > 0 else 0.0

    # --- Determine severity ---
    severity = "low"
    for level in ("high", "medium", "low"):
        if any(kw in text_lower for kw in SEVERITY_KEYWORDS[level]):
            severity = level
            break  # "high" is checked first, so it wins if present

    return ClassificationResult(
        event_type=best_category,
        event_type_score=best_score,
        event_type_confidence=round(confidence, 2),
        severity=severity,
        matched_keywords=category_matches[best_category],
    )