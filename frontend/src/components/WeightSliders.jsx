// frontend/src/components/WeightSliders.jsx

const METRIC_LABELS = {
  cost: "Cost", delay_reduction: "Delay Reduction", customer_satisfaction: "Customer Satisfaction",
  risk: "Risk (lower better)", revenue_recovered: "Revenue Recovered", supplier_reliability: "Supplier Reliability",
};

export default function WeightSliders({ weights, onChange }) {
  const total = Object.values(weights).reduce((a, b) => a + b, 0);

  function handleSlide(key, value) {
    // Re-normalize the OTHER weights proportionally so the total always
    // stays at 1.0 -- required because ScoringWeights (Phase 8) validates
    // this on the backend, and a set of sliders that silently drifts away
    // from summing to 1.0 would start producing backend errors.
    const newValue = parseFloat(value);
    const remaining = 1 - newValue;
    const othersSum = total - weights[key];
    const updated = { ...weights, [key]: newValue };
    for (const k of Object.keys(weights)) {
      if (k !== key) {
        updated[k] = othersSum > 0 ? (weights[k] / othersSum) * remaining : remaining / (Object.keys(weights).length - 1);
      }
    }
    onChange(updated);
  }

  return (
    <div style={{ border: "1px solid #ddd", padding: "1rem", marginBottom: "1rem", borderRadius: 8 }}>
      <h3>Business Priorities</h3>
      <p style={{ fontSize: "0.85rem", color: "#666" }}>
        Adjust these and watch the recommendation update live.
      </p>
      {Object.entries(weights).map(([key, value]) => (
        <div key={key} style={{ marginBottom: "0.5rem" }}>
          <label>{METRIC_LABELS[key]}: {(value * 100).toFixed(0)}%</label>
          <input
            type="range" min="0" max="1" step="0.01" value={value}
            onChange={(e) => handleSlide(key, e.target.value)}
            style={{ width: "100%" }}
          />
        </div>
      ))}
    </div>
  );
}
