# scripts/profile_agent_run.py
"""
Profiles a single end-to-end agent.process_event() call.
Run this BEFORE making any performance changes, save the output,
then run it again AFTER changes to verify actual improvement.
"""

import sys, os, cProfile, pstats, io
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from supply_chain_agent.models import SessionLocal
from supply_chain_agent.ingestion.schemas import EventCreate
from supply_chain_agent.ingestion.event_ingestion import ingest_event
from supply_chain_agent.orchestrator.agent_orchestrator import SupplyChainAgent


def run_once():
    session = SessionLocal()
    payload = EventCreate(
        source="manual",
        raw_text="Acme Electronics reports a 10-day delay on Microcontroller Chip shipment due to a factory fire.",
    )
    event = ingest_event(session, payload)
    agent = SupplyChainAgent(session)
    agent.process_event(event.id)
    session.close()


if __name__ == "__main__":
    profiler = cProfile.Profile()
    profiler.enable()
    run_once()
    profiler.disable()

    stream = io.StringIO()
    stats = pstats.Stats(profiler, stream=stream).sort_stats("cumulative")
    stats.print_stats(20)  # top 20 functions by cumulative time
    print(stream.getvalue())