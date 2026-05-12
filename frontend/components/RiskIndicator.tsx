interface RiskIndicatorProps {
  riskScore: number;
}

function riskLevel(score: number) {
  if (score === 0) return { label: "Low", color: "text-green-400" };
  if (score <= 30) return { label: "Medium", color: "text-yellow-400" };
  if (score <= 60) return { label: "High", color: "text-orange-400" };
  return { label: "Critical", color: "text-red-400" };
}

export default function RiskIndicator({ riskScore }: RiskIndicatorProps) {
  const { label, color } = riskLevel(riskScore);
  return (
    <div className={`text-sm font-medium ${color}`}>
      {label}
      <span className="text-[#888] text-xs ml-1">({riskScore}pts)</span>
    </div>
  );
}
