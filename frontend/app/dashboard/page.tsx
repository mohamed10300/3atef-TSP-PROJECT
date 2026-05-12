"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { Event } from "@/lib/types";
import EventTable from "@/components/EventTable";

const STATUS_FILTERS = ["All", "approved", "rejected", "pending"];
const TYPE_FILTERS = ["All", "medical", "pharma", "health", "tech", "industrial", "business"];

export default function DashboardPage() {
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState("All");
  const [typeFilter, setTypeFilter] = useState("All");

  useEffect(() => {
    api.listEvents({
      status: statusFilter !== "All" ? statusFilter : undefined,
      type: typeFilter !== "All" ? typeFilter : undefined,
    }).then(setEvents).finally(() => setLoading(false));
  }, [statusFilter, typeFilter]);

  const approved = events.filter((e) => e.status === "approved").length;
  const rejected = events.filter((e) => e.status === "rejected").length;
  const pending = events.filter((e) => e.status === "pending").length;

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-xl font-semibold text-[#f5f5f5]">Events</h1>
          <p className="text-sm text-[#555] mt-0.5">All discovered and processed events</p>
        </div>
        <a
          href="/dashboard/upload"
          className="px-4 py-2 bg-[#3b82f6] text-white text-sm font-medium rounded-md hover:bg-blue-500 transition-colors"
        >
          + New Run
        </a>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        {[
          { label: "Total", value: events.length, color: "text-[#f5f5f5]" },
          { label: "Approved", value: approved, color: "text-green-400" },
          { label: "Rejected", value: rejected, color: "text-red-400" },
          { label: "Pending", value: pending, color: "text-yellow-400" },
        ].map(({ label, value, color }) => (
          <div key={label} className="bg-[#111] border border-[#1a1a1a] rounded-lg p-4">
            <div className="text-xs text-[#888] uppercase tracking-wider">{label}</div>
            <div className={`text-2xl font-bold mt-1 ${color}`}>{value}</div>
          </div>
        ))}
      </div>

      {/* Filters */}
      <div className="flex gap-3 mb-4 flex-wrap">
        <div className="flex gap-1">
          {STATUS_FILTERS.map((s) => (
            <button
              key={s}
              onClick={() => setStatusFilter(s)}
              className={`px-3 py-1 text-xs rounded-md transition-colors capitalize ${
                statusFilter === s ? "bg-[#3b82f6] text-white" : "bg-[#111] border border-[#222] text-[#888] hover:text-[#f5f5f5]"
              }`}
            >
              {s}
            </button>
          ))}
        </div>
        <div className="flex gap-1 flex-wrap">
          {TYPE_FILTERS.map((t) => (
            <button
              key={t}
              onClick={() => setTypeFilter(t)}
              className={`px-3 py-1 text-xs rounded-md transition-colors capitalize ${
                typeFilter === t ? "bg-[#1a1a1a] border border-[#3b82f6] text-[#3b82f6]" : "bg-[#111] border border-[#222] text-[#888] hover:text-[#f5f5f5]"
              }`}
            >
              {t}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="text-center py-16 text-[#555]">Loading events…</div>
      ) : (
        <EventTable events={events} />
      )}
    </div>
  );
}
