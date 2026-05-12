"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { Event } from "@/lib/types";
import EventTable from "@/components/EventTable";

export default function EventsPage() {
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.listEvents().then(setEvents).finally(() => setLoading(false));
  }, []);

  return (
    <div className="p-8">
      <h1 className="text-xl font-semibold text-[#f5f5f5] mb-6">All Events</h1>
      {loading ? (
        <div className="text-center py-16 text-[#555]">Loading…</div>
      ) : (
        <EventTable events={events} />
      )}
    </div>
  );
}
