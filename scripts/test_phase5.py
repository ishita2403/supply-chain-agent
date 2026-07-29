
import sys; sys.path.append('src')
from supply_chain_agent.models import SessionLocal
from supply_chain_agent.ingestion.event_ingestion import ingest_from_csv
from supply_chain_agent.understanding.understanding_engine import process_all_raw_events

session = SessionLocal()
ingest_from_csv(session, 'data/sample_events.csv')
results = process_all_raw_events(session)
for e in results:
    print(e.id, e.event_type, e.severity, e.supplier_id, e.component_id, e.confidence_score)
