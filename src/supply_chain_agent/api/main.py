# src/supply_chain_agent/api/main.py  (MODIFY)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import events

app = FastAPI(title="Supply Chain Decision Intelligence Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite's default dev server port
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(events.router)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/events")
def list_events(limit: int = 20):
    """Lists recent events -- used by the frontend's event picker."""
    from .routes.events import get_db
    from ..models import Event
    db = next(get_db())
    events_list = db.query(Event).order_by(Event.id.desc()).limit(limit).all()
    return [
        {"id": e.id, "raw_text": e.raw_text, "status": e.status, "event_type": e.event_type}
        for e in events_list
    ]

from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {
        "message": "Supply Chain Agent API is running"
    }