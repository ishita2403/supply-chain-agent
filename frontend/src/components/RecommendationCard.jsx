export default function RecommendationCard({ recommendation }) {
  const statusColor =
    recommendation.decision_status === "auto_approved"
      ? "#28a745"
      : "#fd7e14";

  return (
    <section
      className="recommendation-card"
      style={{
        marginBottom: "1.5rem",
        padding: "1rem",
        borderRadius: 8,
        background: "#f8f9fa",
        border: `2px solid ${statusColor}`,
      }}
    >
      <h2>Recommendation</h2>

      <p className="recommendation-strategy">
        <strong>
          {recommendation.selected_strategy_type.replace(/_/g, " ")}
        </strong>
      </p>

      <p className="recommendation-confidence">
        Confidence:{" "}
        <strong>{recommendation.confidence_label}</strong>{" "}
        ({recommendation.overall_confidence})
      </p>

      <p className="recommendation-status">
        Status:{" "}
        <span style={{ color: statusColor }}>
          {recommendation.decision_status}
        </span>
      </p>

      {recommendation.guardrail_flags.length > 0 && (
        <ul className="recommendation-flags">
          {recommendation.guardrail_flags.map((f, i) => (
            <li key={i}>{f.message}</li>
          ))}
        </ul>
      )}
    </section>
  );
}