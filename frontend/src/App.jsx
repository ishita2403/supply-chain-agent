// frontend/src/App.jsx

import { useState, useEffect } from "react";
import { fetchEvents, runAgent } from "./api/client";
import EventSelector from "./components/EventSelector";
import AgentRunView from "./components/AgentRunView";
import WeightSliders from "./components/WeightSliders";

const DEFAULT_WEIGHTS = {
  cost: 0.20, delay_reduction: 0.25, customer_satisfaction: 0.20,
  risk: 0.15, revenue_recovered: 0.15, supplier_reliability: 0.05,
};

export default function App() {
  const [events, setEvents] = useState([]);
  const [selectedEventId, setSelectedEventId] = useState(null);
  const [weights, setWeights] = useState(DEFAULT_WEIGHTS);
  const [run, setRun] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchEvents().then(setEvents);
  }, []);

  useEffect(() => {
    if (selectedEventId === null) return;
    setLoading(true);
    runAgent(selectedEventId, weights)
      .then(setRun)
      .finally(() => setLoading(false));
  }, [selectedEventId, weights]);

  return (
    <div style={{ maxWidth: 1000, margin: "0 auto", padding: "1.5rem", fontFamily: "sans-serif" }}>
      <h1>Supply Chain Decision Intelligence Agent</h1>

      <EventSelector events={events} selectedEventId={selectedEventId} onSelect={setSelectedEventId} />

      {selectedEventId && (
        <WeightSliders weights={weights} onChange={setWeights} />
      )}

      {loading && <p>Agent is analyzing...</p>}
      {run && !loading && <AgentRunView run={run} />}
    </div>
  );
}