"use client";
import Link from "next/link";
import type { Event } from "@/lib/types";
import ApprovalStatus from "./ApprovalStatus";
import ScoreBadge from "./ScoreBadge";
import RiskIndicator from "./RiskIndicator";

interface EventTableProps {
  events: Event[];
}

export default function EventTable({ events }: EventTableProps) {
  if (!events.length) {
    return (
      <div className="text-center py-16 text-[#555] text-sm">
        No events found. Upload an Excel sheet or trigger a pipeline run to get started.
      </div>
    );
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-[#222]">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-[#222] bg-[#111]">
            {["Event", "Type", "Dates", "Location", "Status", "Score", "Risk", ""].map((h) => (
              <th key={h} className="px-4 py-3 text-left text-xs font-medium text-[#888] uppercase tracking-wider whitespace-nowrap">
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {events.map((event, i) => (
            <tr
              key={event.id}
              className={`border-b border-[#1a1a1a] hover:bg-[#111] transition-colors ${i % 2 === 0 ? "bg-[#0d0d0d]" : "bg-[#0a0a0a]"}`}
            >
              <td className="px-4 py-3 max-w-[200px]">
                <div className="font-medium text-[#f5f5f5] truncate">{event.name}</div>
                <div className="text-xs text-[#555] mt-0.5">{event.source}</div>
              </td>
              <td className="px-4 py-3">
                <span className="px-2 py-0.5 bg-[#1a1a1a] border border-[#2a2a2a] rounded text-xs text-[#aaa] capitalize">
                  {event.type}
                </span>
              </td>
              <td className="px-4 py-3 whitespace-nowrap text-[#aaa] text-xs">
                {event.start_date ? (
                  <>
                    <div>{event.start_date}</div>
                    <div className="text-[#555]">→ {event.end_date}</div>
                  </>
                ) : (
                  <span className="text-[#444]">N/A</span>
                )}
              </td>
              <td className="px-4 py-3 whitespace-nowrap text-[#aaa] text-xs">
                {event.city}{event.city && event.country ? ", " : ""}{event.country}
              </td>
              <td className="px-4 py-3">
                <ApprovalStatus status={event.status} size="sm" />
              </td>
              <td className="px-4 py-3">
                <ScoreBadge score={event.score} />
              </td>
              <td className="px-4 py-3">
                <RiskIndicator riskScore={event.risk_score} />
              </td>
              <td className="px-4 py-3 text-right">
                <Link
                  href={`/dashboard/events/${event.id}`}
                  className="text-xs text-[#3b82f6] hover:text-blue-300 transition-colors"
                >
                  View →
                </Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
