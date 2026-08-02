// frontend/src/components/RecoveryPlansPanel.jsx

import ScoreBreakdownChart from "./ScoreBreakdownChart";

export default function RecoveryPlansPanel({ scoredPlans }) {
  return (
    <section style={{ marginBottom: "1.5rem" }}>
      <h2>Recovery Plans Considered ({scoredPlans.length})</h2>
      {scoredPlans.map((sp, idx) => (
        <details key={sp.plan_id} open={idx === 0} style={{
          border: "1px solid #eee", borderRadius: 6, padding: "0.5rem 1rem", marginBottom: "0.5rem",
        }}>
          <summary>
            <strong>{sp.strategy_type.replace(/_/g, " ")}</strong> — score {sp.overall_score.toFixed(3)}
            {idx === 0 && <span style={{ color: "#28a745" }}> (top ranked)</span>}
          </summary>
          <ScoreBreakdownChart breakdown={sp.score_breakdown} />
        </details>
      ))}
    </section>
  );
}