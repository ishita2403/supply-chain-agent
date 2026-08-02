import sys, os
sys.path.append(os.path.join(os.getcwd(), 'src'))
from sqlalchemy import create_engine
from supply_chain_agent.models import Base, SessionLocal
from tests.scenarios.scenario_seed_data import build_rich_seed
from supply_chain_agent.ingestion.schemas import EventCreate
from supply_chain_agent.ingestion.event_ingestion import ingest_event
from supply_chain_agent.orchestrator.agent_orchestrator import SupplyChainAgent

engine = create_engine('sqlite:///:memory:')
Base.metadata.create_all(engine)
SessionLocal.configure(bind=engine)
session = SessionLocal()
build_rich_seed(session)
payload = EventCreate(source='manual', raw_text='Acme Electronics reports a 10-day delay on Microcontroller Chip ... product made at two factories.')
event = ingest_event(session, payload)
agent = SupplyChainAgent(session)
run = agent.process_event(event.id)
print('status', run.status)
print('event status', run.event.status)
print('report affected products', run.report.affected_product_names)
print('plans', [p.strategy_type for p in run.plans])
print('reason', run.stop_reason)
