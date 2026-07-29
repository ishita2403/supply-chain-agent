# src/supply_chain_agent/understanding/keyword_rules.py

"""
Keyword -> category knowledge base for rule-based event classification.
Each keyword carries a weight: more specific/unambiguous phrases get
higher weight than generic ones, so scoring reflects real confidence,
not just keyword count.
"""

EVENT_TYPE_KEYWORDS = {
    "supplier_delay": [
        ("10-day delay", 5),
        ("delay", 4),
        ("late", 2),
        ("behind schedule", 4),
        ("postponed", 3),
        ("pushed back", 3),
        ("shipment", 1),
        ("supplier", 1),
    ],

    "quality_issue": [
        ("defect", 2),
        ("quality", 1),
        ("reject", 2),
        ("non-conforming", 3),
        ("failed inspection", 3),
        ("defect rate", 3),
    ],

    "factory_shutdown": [
        ("shutdown", 4),
        ("shut down", 4),
        ("halt production", 4),
        ("explosion", 4),
        ("strike", 3),

        # Notice "fire" is intentionally a smaller signal
        ("fire", 1),
        ("closed", 1),
    ],

    "transportation_delay": [
        ("shipping delay", 4),
        ("port congestion", 3),
        ("customs", 2),
        ("logistics delay", 3),
        ("in transit", 1),
        ("vessel delay", 3),
    ],

    "engineering_change": [
        ("engineering change", 3),
        ("ecn", 3),
        ("design change", 3),
        ("spec change", 2),
        ("revised specification", 3),
    ],

    "inventory_shortage": [
        ("shortage", 3),
        ("stockout", 3),
        ("out of stock", 3),
        ("insufficient inventory", 3),
        ("low stock", 2),
    ],

    "supplier_failure": [
        ("bankruptcy", 3),
        ("insolvent", 3),
        ("ceased operations", 3),
        ("supplier failure", 3),
        ("went out of business", 3),
    ],
}

# Severity keywords apply ACROSS categories — e.g. "fire" implies high
# severity regardless of which category it fell into.
SEVERITY_KEYWORDS = {
    "high": ["fire", "shutdown", "bankruptcy", "insolvent", "explosion",
             "halt production", "ceased operations", "strike"],
    "medium": ["delay", "defect", "shortage", "congestion", "postponed"],
    "low": ["minor", "slight", "on-time", "confirmed on-time", "resolved"],
}