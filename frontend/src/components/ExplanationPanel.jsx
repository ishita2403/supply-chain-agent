// frontend/src/components/ExplanationPanel.jsx

export default function ExplanationPanel({ explanation }) {
  if (!explanation) return null;

  return (
    <div style={{ border: "1px solid #ddd", borderRadius: 8, padding: "1rem", marginTop: "1rem" }}>
      <h3>Explanation</h3>

      <p>
        <strong>Source:</strong> {explanation.narrative_source}
      </p>

      <p>{explanation.narrative}</p>

      <h4>Reasoning Trace</h4>
      <ul>
        {explanation.reasoning_trace?.map((line, index) => (
          <li key={index}>{line}</li>
        ))}
      </ul>
    </div>
  );
}