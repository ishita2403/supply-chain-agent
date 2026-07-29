# src/supply_chain_agent/scoring/normalizer.py

def normalize_metric(values: dict[str, float], higher_is_better: bool) -> dict[str, float]:
    """
    Min-max normalizes a metric across all plans to a 0-1 scale, where
    1.0 always means 'best' and 0.0 always means 'worst', REGARDLESS of
    whether the raw metric is naturally 'higher is better' (satisfaction)
    or 'lower is better' (cost, risk) -- the inversion happens here so
    every downstream consumer can just do weight * normalized_value.
    """
    if not values:
        return {}

    raw = list(values.values())
    lo, hi = min(raw), max(raw)

    if hi == lo:
        # No variation across plans on this metric -- it can't
        # meaningfully differentiate them, so treat everyone as neutral.
        return {plan_id: 0.5 for plan_id in values}

    normalized = {}
    for plan_id, val in values.items():
        scaled = (val - lo) / (hi - lo)  # 0 = worst raw value, 1 = best raw value (if higher_is_better)
        normalized[plan_id] = scaled if higher_is_better else (1 - scaled)

    return normalized