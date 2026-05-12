"use client";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { api } from "@/lib/api";
import type { Event, Report } from "@/lib/types";
import ApprovalStatus from "@/components/ApprovalStatus";
import ScoreBadge from "@/components/ScoreBadge";
import RiskIndicator from "@/components/RiskIndicator";
import HotelComparisonTable from "@/components/HotelComparisonTable";

export default function EventDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [event, setEvent] = useState<Event | null>(null);
  const [report, setReport] = useState<Report | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([api.getEvent(id), api.getEventReport(id).catch(() => null)]).then(([ev, rpt]) => {
      setEvent(ev);
      setReport(rpt);
    }).finally(() => setLoading(false));
  }, [id]);

  if (loading) return <div className="p-8 text-[#555]">Loading event…</div>;
  if (!event) return <div className="p-8 text-red-400">Event not found.</div>;

  const latestDecision = event.decisions?.[event.decisions.length - 1];

  return (
    <div className="p-8 max-w-5xl">
      {/* Breadcrumb */}
      <div className="text-xs text-[#555] mb-6">
        <Link href="/dashboard" className="hover:text-[#888]">Dashboard</Link>
        <span className="mx-2">→</span>
        <span className="text-[#888]">{event.name}</span>
      </div>

      {/* Header */}
      <div className="flex items-start justify-between gap-4 mb-8">
        <div>
          <h1 className="text-2xl font-bold text-[#f5f5f5]">{event.name}</h1>
          <div className="text-sm text-[#888] mt-1">
            {event.city}{event.city && event.country ? ", " : ""}{event.country}
            {event.venue_name ? ` · ${event.venue_name}` : ""}
          </div>
          {event.start_date && (
            <div className="text-sm text-[#555] mt-0.5">
              {event.start_date} → {event.end_date}
            </div>
          )}
        </div>
        <ApprovalStatus status={event.status} size="lg" />
      </div>

      {/* Score Panel */}
      <div className="grid grid-cols-3 gap-4 mb-8">
        <div className="bg-[#111] border border-[#1a1a1a] rounded-lg p-4">
          <div className="text-xs text-[#888] uppercase tracking-wider mb-2">Profitability Score</div>
          <ScoreBadge score={event.score} />
        </div>
        <div className="bg-[#111] border border-[#1a1a1a] rounded-lg p-4">
          <div className="text-xs text-[#888] uppercase tracking-wider mb-2">Risk Score</div>
          <RiskIndicator riskScore={event.risk_score} />
        </div>
        <div className="bg-[#111] border border-[#1a1a1a] rounded-lg p-4">
          <div className="text-xs text-[#888] uppercase tracking-wider mb-2">Event Type</div>
          <span className="px-2 py-0.5 bg-[#1a1a1a] border border-[#2a2a2a] rounded text-sm text-[#aaa] capitalize">
            {event.type}
          </span>
        </div>
      </div>

      {/* Approval Decision */}
      {latestDecision && (
        <div className="bg-[#111] border border-[#1a1a1a] rounded-lg p-4 mb-8">
          <div className="text-xs text-[#888] uppercase tracking-wider mb-3">Approval Decision</div>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-[#555]">Rule: </span>
              <span className="text-[#aaa] font-mono">{latestDecision.rule_triggered}</span>
            </div>
            <div>
              <span className="text-[#555]">Hotels cheaper by ≥$4: </span>
              <span className={`font-bold ${latestDecision.hotels_cheaper_count >= 3 ? "text-green-400" : "text-red-400"}`}>
                {latestDecision.hotels_cheaper_count}
              </span>
              <span className="text-[#555]"> / 3 required</span>
            </div>
            <div>
              <span className="text-[#555]">Min price difference: </span>
              <span className="text-[#aaa] font-mono">${latestDecision.min_price_difference.toFixed(2)}</span>
            </div>
            <div>
              <span className="text-[#555]">Decided by: </span>
              <span className="text-[#aaa]">{latestDecision.decided_by}</span>
            </div>
          </div>
        </div>
      )}

      {/* Hotel Comparison */}
      <div className="mb-8">
        <h2 className="text-base font-semibold text-[#f5f5f5] mb-3">Hotel Comparison</h2>
        <HotelComparisonTable hotels={event.hotels ?? []} />
      </div>

      {/* Report Download */}
      {report && (
        <div className="bg-[#111] border border-[#1a1a1a] rounded-lg p-4 flex items-center justify-between">
          <div>
            <div className="text-sm font-medium text-[#f5f5f5]">Generated Report</div>
            <div className="text-xs text-[#555] mt-0.5">{report.report_type} · {new Date(report.generated_at).toLocaleDateString()}</div>
          </div>
          <a
            href={api.getReportExportUrl(report.id)}
            target="_blank"
            rel="noopener noreferrer"
            className="px-4 py-2 bg-[#3b82f6] text-white text-sm rounded-md hover:bg-blue-500 transition-colors"
          >
            Download PDF
          </a>
        </div>
      )}
    </div>
  );
}
