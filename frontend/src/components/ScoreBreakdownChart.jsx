// frontend/src/components/ScoreBreakdownChart.jsx

import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

export default function ScoreBreakdownChart({ breakdown }) {
  const data = Object.entries(breakdown).map(([metric, c]) => ({
    metric, contribution: Number(c.contribution.toFixed(3)),
  }));
  return (
    <ResponsiveContainer width="100%" height={180}>
      <BarChart data={data} layout="vertical" margin={{ left: 40 }}>
        <XAxis type="number" domain={[0, "auto"]} />
        <YAxis type="category" dataKey="metric" width={130} />
        <Tooltip />
        <Bar dataKey="contribution" fill="#4a90d9" />
      </BarChart>
    </ResponsiveContainer>
  );
}