"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { Report } from "@/lib/types";
import ReportCard from "@/components/ReportCard";

const TYPES = ["All", "approved_events", "rejected_events", "competitor_analysis", "hotel_profitability", "risk_summary"];

export default function ReportsPage() {
  const [reports, setReports] = useState<Report[]>([]);
  const [loading, setLoading] = useState(true);
  const [typeFilter, setTypeFilter] = useState("All");

  useEffect(() => {
    api.listReports().then(setReports).finally(() => setLoading(false));
  }, []);

  const filtered = typeFilter === "All" ? reports : reports.filter((r) => r.report_type === typeFilter);

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-xl font-semibold text-[#f5f5f5]">Reports</h1>
          <p className="text-sm text-[#555] mt-0.5">{reports.length} generated reports</p>
        </div>
      </div>

      {/* Type filter */}
      <div className="flex gap-2 flex-wrap mb-6">
        {TYPES.map((t) => (
          <button
            key={t}
            onClick={() => setTypeFilter(t)}
            className={`px-3 py-1 text-xs rounded-md transition-colors ${
              typeFilter === t ? "bg-[#3b82f6] text-white" : "bg-[#111] border border-[#222] text-[#888] hover:text-[#f5f5f5]"
            }`}
          >
            {t === "All" ? "All" : t.replace(/_/g, " ")}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="text-center py-16 text-[#555]">Loading reports…</div>
      ) : filtered.length === 0 ? (
        <div className="text-center py-16 text-[#555] text-sm">No reports found.</div>
      ) : (
        <div className="space-y-3">
          {filtered.map((r) => <ReportCard key={r.id} report={r} />)}
        </div>
      )}
    </div>
  );
}
