import type { Report } from "@/lib/types";
import { api } from "@/lib/api";

interface ReportCardProps {
  report: Report;
}

const reportTypeLabels: Record<string, string> = {
  approved_events: "Approved Events",
  rejected_events: "Rejected Events",
  competitor_analysis: "Competitor Analysis",
  hotel_profitability: "Hotel Profitability",
  risk_summary: "Risk Summary",
};

export default function ReportCard({ report }: ReportCardProps) {
  const label = reportTypeLabels[report.report_type] ?? report.report_type;
  const date = new Date(report.generated_at).toLocaleDateString("en-US", {
    year: "numeric", month: "short", day: "numeric",
  });

  return (
    <div className="bg-[#111] border border-[#222] rounded-lg p-4 flex items-center justify-between gap-4">
      <div>
        <div className="text-sm font-medium text-[#f5f5f5]">{label}</div>
        <div className="text-xs text-[#888] mt-0.5">{date}</div>
        <div className="text-xs text-[#555] mt-0.5">{report.id.slice(0, 8)}…</div>
      </div>
      <a
        href={api.getReportExportUrl(report.id)}
        target="_blank"
        rel="noopener noreferrer"
        className="shrink-0 px-3 py-1.5 bg-[#1a1a1a] border border-[#333] text-sm text-[#f5f5f5] rounded-md hover:bg-[#222] transition-colors"
      >
        Download PDF
      </a>
    </div>
  );
}
