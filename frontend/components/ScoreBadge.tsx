interface ScoreBadgeProps {
  score: number;
  label?: string;
}

function scoreColor(score: number) {
  if (score >= 70) return { bar: "bg-green-500", text: "text-green-400" };
  if (score >= 40) return { bar: "bg-yellow-500", text: "text-yellow-400" };
  return { bar: "bg-red-500", text: "text-red-400" };
}

export default function ScoreBadge({ score, label = "Score" }: ScoreBadgeProps) {
  const { bar, text } = scoreColor(score);
  return (
    <div className="flex flex-col gap-1 w-full max-w-[120px]">
      <div className="flex justify-between items-center">
        <span className="text-xs text-[#888]">{label}</span>
        <span className={`text-xs font-semibold ${text}`}>{score.toFixed(0)}</span>
      </div>
      <div className="w-full bg-[#222] rounded-full h-1.5">
        <div
          className={`h-1.5 rounded-full transition-all ${bar}`}
          style={{ width: `${Math.min(score, 100)}%` }}
        />
      </div>
    </div>
  );
}
