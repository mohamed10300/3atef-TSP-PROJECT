"use client";
import { useEffect, useState, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { api } from "@/lib/api";
import type { Hotel } from "@/lib/types";
import HotelComparisonTable from "@/components/HotelComparisonTable";

function HotelsContent() {
  const searchParams = useSearchParams();
  const eventId = searchParams.get("event_id") ?? undefined;
  const [hotels, setHotels] = useState<Hotel[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.listHotels(eventId).then(setHotels).finally(() => setLoading(false));
  }, [eventId]);

  const cheaper = hotels.filter((h) => h.is_cheaper_than_vendor).length;

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-xl font-semibold text-[#f5f5f5]">Hotels</h1>
          <p className="text-sm text-[#555] mt-0.5">
            {hotels.length} hotels · {cheaper} cheaper than vendor by ≥$4
          </p>
        </div>
      </div>
      {loading ? (
        <div className="text-center py-16 text-[#555]">Loading hotels…</div>
      ) : (
        <HotelComparisonTable hotels={hotels} />
      )}
    </div>
  );
}

export default function HotelsPage() {
  return (
    <Suspense fallback={<div className="text-center py-16 text-[#555]">Loading…</div>}>
      <HotelsContent />
    </Suspense>
  );
}
