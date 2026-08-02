# tests/scenarios/test_scenarios.py

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))

import pytest
from supply_chain_agent.ingestion.schemas import EventCreate
from supply_chain_agent.ingestion.event_ingestion import ingest_event
from supply_chain_agent.orchestrator.agent_orchestrator import SupplyChainAgent
from .scenario_seed_data import build_rich_seed
from .scenario_definitions import SCENARIOS

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from conftest import isolated_session  # reuse the shared fixture


@pytest.mark.parametrize("scenario", SCENARIOS, ids=[s.name for s in SCENARIOS])
def test_scenario(isolated_session, scenario):
    build_rich_seed(isolated_session)

    payload = EventCreate(source="manual", raw_text=scenario.raw_text)
    event = ingest_event(isolated_session, payload)

    agent = SupplyChainAgent(isolated_session)
    run = agent.process_event(event.id)

    failures = []
    for expectation in scenario.expectations:
        passed, message = expectation(run)
        if not passed:
            failures.append(message)

    assert not failures, (
        f"Scenario '{scenario.name}' ({scenario.description}) failed:\n" + "\n".join(failures)
    )
    