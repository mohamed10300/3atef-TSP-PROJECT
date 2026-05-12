import type { Hotel } from "@/lib/types";

interface HotelComparisonTableProps {
  hotels: Hotel[];
}

function DiffCell({ diff }: { diff: number }) {
  const cheaper = diff <= -4;
  const color = cheaper ? "text-green-400" : diff < 0 ? "text-yellow-400" : "text-red-400";
  return (
    <span className={`font-mono text-sm ${color}`}>
      {diff > 0 ? "+" : ""}${diff.toFixed(2)}
    </span>
  );
}

export default function HotelComparisonTable({ hotels }: HotelComparisonTableProps) {
  if (!hotels.length) {
    return <div className="text-[#555] text-sm py-8 text-center">No hotel data yet.</div>;
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-[#222]">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-[#222] bg-[#111]">
            {["Hotel", "Distance", "Market $", "Vendor $", "Diff", "Competitor $", "Rating", "Available", "Policy Risk"].map((h) => (
              <th key={h} className="px-4 py-3 text-left text-xs font-medium text-[#888] uppercase tracking-wider whitespace-nowrap">
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {hotels.map((hotel, i) => (
            <tr
              key={hotel.id}
              className={`border-b border-[#1a1a1a] ${hotel.is_cheaper_than_vendor ? "bg-green-950/10" : i % 2 === 0 ? "bg-[#0d0d0d]" : "bg-[#0a0a0a]"} hover:bg-[#111] transition-colors`}
            >
              <td className="px-4 py-3 max-w-[180px]">
                <div className="font-medium text-[#f5f5f5] truncate">{hotel.name}</div>
                {hotel.room_type && <div className="text-xs text-[#555]">{hotel.room_type}</div>}
              </td>
              <td className="px-4 py-3 text-[#aaa] text-xs whitespace-nowrap">
                {hotel.distance_from_venue_km ? `${hotel.distance_from_venue_km.toFixed(1)} km` : "—"}
              </td>
              <td className="px-4 py-3 font-mono text-[#f5f5f5]">
                ${hotel.market_price.toFixed(2)}
              </td>
              <td className="px-4 py-3 font-mono text-[#aaa]">
                {hotel.vendor_price > 0 ? `$${hotel.vendor_price.toFixed(2)}` : "—"}
              </td>
              <td className="px-4 py-3">
                {hotel.vendor_price > 0 ? <DiffCell diff={hotel.price_difference} /> : <span className="text-[#444]">—</span>}
              </td>
              <td className="px-4 py-3 font-mono text-[#aaa]">
                {hotel.competitor_price > 0 ? `$${hotel.competitor_price.toFixed(2)}` : "—"}
              </td>
              <td className="px-4 py-3 text-[#aaa]">
                {hotel.rating > 0 ? (
                  <span className="text-yellow-400">★ {hotel.rating.toFixed(1)}</span>
                ) : "—"}
              </td>
              <td className="px-4 py-3">
                {hotel.availability ? (
                  <span className="text-green-400 text-xs">Yes</span>
                ) : (
                  <span className="text-red-400 text-xs">No</span>
                )}
              </td>
              <td className="px-4 py-3 max-w-[160px]">
                <div className="text-xs text-[#888] truncate" title={hotel.refund_policy}>
                  {hotel.refund_policy || "—"}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
