def compute_severity_from_delay_and_priority(max_delay_days: int, high_priority_customers_affected: int) -> str:
    if max_delay_days >= 14 or high_priority_customers_affected >= 2:
        return "critical"
    if max_delay_days >= 7 or high_priority_customers_affected >= 1:
        return "high"
    if max_delay_days >= 3:
        return "medium"
    return "low"