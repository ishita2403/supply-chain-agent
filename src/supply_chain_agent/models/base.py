# src/supply_chain_agent/models/base.py

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# The path to our local SQLite database file.
# Using a relative path keeps this portable across machines.
DATABASE_URL = "sqlite:///./data/supply_chain.db"

# The engine is SQLAlchemy's connection to the actual database.
# echo=False keeps SQL logging off; set True temporarily if you want to
# see every SQL statement SQLAlchemy generates (great for debugging).
engine = create_engine(DATABASE_URL, echo=False)

# Base is the class every model (Supplier, Product, etc.) will inherit from.
# SQLAlchemy uses this to know which classes map to which tables.
Base = declarative_base()

# SessionLocal is a factory for creating database "sessions" — a session
# is basically a workspace where you add/query/commit changes.
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)