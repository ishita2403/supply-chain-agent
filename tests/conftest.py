# tests/conftest.py

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from supply_chain_agent.models import Base


@pytest.fixture
def isolated_session():
    """
    Provides a fresh, in-memory SQLite database for a single test,
    automatically discarded afterward. This prevents scenario tests from
    contaminating each other or the shared data/supply_chain.db file used
    for manual exploration (Section 2.4).
    """
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()