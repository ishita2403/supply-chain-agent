# src/supply_chain_agent/impact/delay_estimator.py

import re

# Fallback defaults when no explicit number is found in the event text,
# keyed by (event_type, severity). These are reasonable industry-plausible
# defaults, not scientifically derived — worth stating plainly if asked.
DEFAULT_DELAY_DAYS = {
    ("supplier_delay", "high"): 14,
    ("supplier_delay", "medium"): 7,
    ("supplier_delay", "low"): 2,
    ("factory_shutdown", "high"): 21,
    ("factory_shutdown", "medium"): 10,
    ("factory_shutdown", "low"): 5,
    ("transportation_delay", "high"): 10,
    ("transportation_delay", "medium"): 5,
    ("transportation_delay", "low"): 2,
    ("quality_issue", "high"): 7,
    ("quality_issue", "medium"): 3,
    ("quality_issue", "low"): 1,
    ("inventory_shortage", "high"): 10,
    ("inventory_shortage", "medium"): 5,
    ("inventory_shortage", "low"): 2,
    ("supplier_failure", "high"): 30,
    ("engineering_change", "medium"): 5,
}

NUMBER_DAY_PATTERN = re.compile(r"(\d+)\s*[-\s]?\s*day", re.IGNORECASE)


def estimate_source_delay_days(raw_text: str, event_type: str, severity: str) -> tuple[int, str]:
    """
    Returns (delay_days, method) where method explains HOW we got the number
    - important for the audit trail / explanation engine later.
    """
    match = NUMBER_DAY_PATTERN.search(raw_text)
    if match:
        return int(match.group(1)), "extracted_from_text"

    default = DEFAULT_DELAY_DAYS.get((event_type, severity))
    if default is not None:
        return default, "severity_based_default"

    # Absolute fallback if we have neither a match nor a table entry
    return 3, "generic_fallback"