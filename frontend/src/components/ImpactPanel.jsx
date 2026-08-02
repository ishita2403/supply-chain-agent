// frontend/src/components/ImpactPanel.jsx

export default function ImpactPanel({ report }) {
  const severityColors = { critical: "#dc3545", high: "#fd7e14", medium: "#ffc107", low: "#28a745" };
  return (
    <section style={{ marginBottom: "1.5rem" }}>
      <h2>Impact Analysis</h2>
      <span style={{
        background: severityColors[report.overall_severity], color: "white",
        padding: "0.2rem 0.6rem", borderRadius: 4, fontSize: "0.85rem",
      }}>
        {report.overall_severity.toUpperCase()}
      </span>
      <p>{report.source_delay_days}-day delay affecting {report.affected_pos.length} purchase order(s).</p>
      <p>Total revenue at risk: <strong>${report.total_revenue_at_risk.toLocaleString()}</strong></p>
      <p>Affected products: {report.affected_product_names.join(", ") || "none"}</p>
    </section>
  );
}