import { useState, useEffect } from "react";
import { fetchEvents, runAgent } from "./api/client";
import EventSelector from "./components/EventSelector";
import AgentRunView from "./components/AgentRunView";
import WeightSliders from "./components/WeightSliders";
import "./App.css";

const DEFAULT_WEIGHTS = {
  cost: 0.20,
  delay_reduction: 0.25,
  customer_satisfaction: 0.20,
  risk: 0.15,
  revenue_recovered: 0.15,
  supplier_reliability: 0.05,
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
    <div className="app-background">

      <div className="network-decoration">
        <span className="network-node node-1" />
        <span className="network-node node-2" />
        <span className="network-node node-3" />
        <span className="network-node node-4" />
        <span className="network-node node-5" />
        <span className="network-node node-6" />

        <span className="network-line line-1" />
        <span className="network-line line-2" />
        <span className="network-line line-3" />
        <span className="network-line line-4" />
        <span className="network-line line-5" />
      </div>

      <main className="dashboard-shell">

        <header className="dashboard-header">
          <div className="header-badge">
            Decision Intelligence Platform
          </div>

          <h1>
            Supply Chain Decision Intelligence Agent
          </h1>

          <p>
            Analyze supply chain disruptions, evaluate operational risk,
            and generate data-driven recovery recommendations.
          </p>
        </header>

        <section className="dashboard-panel">

          <div className="selector-section">
            <span className="section-label">
              Supply Chain Event
            </span>

            <EventSelector
              events={events}
              selectedEventId={selectedEventId}
              onSelect={setSelectedEventId}
            />
          </div>

          {selectedEventId && (
            <WeightSliders
              weights={weights}
              onChange={setWeights}
            />
          )}

          {loading && (
            <div className="loading-state">
              <span className="loading-dot" />
              Agent is analyzing the selected event...
            </div>
          )}

          {run && !loading && (
            <AgentRunView run={run} />
          )}

        </section>

      </main>
    </div>
  );
}