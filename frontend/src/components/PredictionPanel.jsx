// frontend/src/components/PredictionPanel.jsx

export default function PredictionPanel({ postState }) {
  return (
    <section style={{ marginBottom: "1.5rem" }}>
      <h2>Projected Outcome</h2>
      <p>{postState.narrative}</p>
      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead><tr><th>PO</th><th>Customer</th><th>Before</th><th>After</th></tr></thead>
        <tbody>
          {postState.projected_pos.map((p) => (
            <tr key={p.po_id} style={{ borderTop: "1px solid #eee" }}>
              <td>#{p.po_id}</td><td>{p.customer_name}</td>
              <td>{p.original_delay_days}d</td>
              <td style={{ color: p.still_at_risk ? "#dc3545" : "#28a745" }}>{p.projected_delay_days}d</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}