# src/supply_chain_agent/api/main.py

from fastapi import FastAPI
from .routes import events

app = FastAPI(title="Supply Chain Decision Intelligence Agent")

app.include_router(events.router)


@app.get("/health")
def health():
    return {"status": "ok"}