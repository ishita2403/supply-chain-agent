// frontend/src/components/AgentRunView.jsx

import ImpactPanel from "./ImpactPanel";
import RecoveryPlansPanel from "./RecoveryPlansPanel";
import RecommendationCard from "./RecommendationCard";
import ExplanationPanel from "./ExplanationPanel";
import PredictionPanel from "./PredictionPanel";

export default function AgentRunView({ run }) {
  if (run.status === "incomplete") {
    return (
      <div style={{ background: "#fff3cd", padding: "1rem", borderRadius: 8 }}>
        <strong>Analysis incomplete.</strong> Stopped at: {run.stopped_at_step}.
        <p>{run.stop_reason}</p>
      </div>
    );
  }

  return (
    <div>
      <ImpactPanel report={run.impact_report} />
      <RecoveryPlansPanel scoredPlans={run.scored_plans} />
      <RecommendationCard recommendation={run.recommendation} />
      <ExplanationPanel explanation={run.explanation} />
      <PredictionPanel postState={run.post_recommendation_state} />
    </div>
  );
}