import sys
import time

sys.path.append("src")

from supply_chain_agent.models import SessionLocal
from supply_chain_agent.ingestion.event_ingestion import ingest_from_csv
from supply_chain_agent.understanding.understanding_engine import process_all_raw_events
from supply_chain_agent.orchestrator.agent_orchestrator import SupplyChainAgent

session = SessionLocal()

# Load sample event
ingest_from_csv(session, "data/sample_events.csv")
events = process_all_raw_events(session)

event = events[0]
agent = SupplyChainAgent(session)

print("=" * 60)

start = time.time()
run = agent.process_event(event.id, skip_llm=True)
print(f"skip_llm=True : {time.time() - start:.3f} sec")

print("=" * 60)

start = time.time()
run = agent.process_event(event.id, skip_llm=False)
print(f"skip_llm=False: {time.time() - start:.3f} sec")