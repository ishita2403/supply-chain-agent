import sys
import os

sys.path.append("src")

from supply_chain_agent.models import SessionLocal, Event
from supply_chain_agent.ingestion.event_ingestion import ingest_from_csv
from supply_chain_agent.understanding.understanding_engine import process_all_raw_events
from supply_chain_agent.impact.impact_analysis import analyze_impact
from supply_chain_agent.recovery.plan_generator import generate_recovery_plans

session = SessionLocal()

# -----------------------------
# Check CSV exists
# -----------------------------
csv_path = "data/sample_events.csv"

print(f"Current working directory: {os.getcwd()}")
print(f"CSV exists: {os.path.exists(csv_path)}")

if not os.path.exists(csv_path):
    raise FileNotFoundError(f"CSV file not found: {csv_path}")

# -----------------------------
# Ingest events
# -----------------------------
print("\nIngesting events...")
ingest_from_csv(session, csv_path)

# -----------------------------
# Process raw events
# -----------------------------
print("\nProcessing raw events...")
events = process_all_raw_events(session)

print(f"New events created: {len(events)}")

# -----------------------------
# If no new events were returned,
# check if events already exist
# -----------------------------
if len(events) == 0:
    print("\nNo new events were processed.")

    existing_events = session.query(Event).all()
    print(f"Existing events in database: {len(existing_events)}")

    if len(existing_events) == 0:
        raise Exception(
            "No events exist in the database. Check your CSV and understanding engine."
        )

    print("Using first existing event from database...")
    event = existing_events[0]
else:
    event = events[0]

print(f"\nSelected Event ID: {event.id}")

# -----------------------------
# Run impact analysis
# -----------------------------
print("\nRunning impact analysis...")
report = analyze_impact(session, event)

# -----------------------------
# Generate recovery plans
# -----------------------------
print("\nGenerating recovery plans...")
plans = generate_recovery_plans(session, event, report)

print("\nRecovery Plans:")
print("-" * 50)

if not plans:
    print("No recovery plans generated.")
else:
    for i, plan in enumerate(plans, start=1):
        print(f"{i}. [{plan.strategy_type}] {plan.description}")