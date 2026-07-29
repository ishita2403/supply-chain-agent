import sys
sys.path.append('src')
from supply_chain_agent.models import SessionLocal
from supply_chain_agent.ingestion.event_ingestion import ingest_from_csv
from supply_chain_agent.understanding.understanding_engine import process_all_raw_events
from supply_chain_agent.impact.impact_analysis import analyze_impact
from supply_chain_agent.recovery.plan_generator import generate_recovery_plans
from supply_chain_agent.simulation.scenario_simulator import simulate_all_plans

session = SessionLocal()
ingest_from_csv(session, 'data/sample_events.csv')
events = process_all_raw_events(session)

event = events[0]
report = analyze_impact(session, event)
plans = generate_recovery_plans(session, event, report)
results = simulate_all_plans(plans, report)

for pid, r in results.items():
    print(f"{pid:35s} cost=${r.cost:>10,.2f}  delay_reduced={r.delay_reduction_days:>4.1f}d  "
          f"revenue_recovered=${r.revenue_recovered:>12,.2f}  risk={r.risk_score:>3.0f}  "
          f"satisfaction={r.customer_satisfaction_score:>3.0f}")
