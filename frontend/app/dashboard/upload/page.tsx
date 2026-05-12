"use client";
import { useState } from "react";
import UploadDropzone from "@/components/UploadDropzone";
import { api } from "@/lib/api";
import type { ExcelUploadResponse } from "@/lib/types";

export default function UploadPage() {
  const [uploadResult, setUploadResult] = useState<ExcelUploadResponse | null>(null);
  const [running, setRunning] = useState(false);
  const [runResult, setRunResult] = useState<string | null>(null);
  const [eventName, setEventName] = useState("");
  const [city, setCity] = useState("");
  const [country, setCountry] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [eventType, setEventType] = useState("medical");

  async function handleRun() {
    if (!uploadResult) return;
    setRunning(true);
    setRunResult(null);
    try {
      const result = await api.runPipeline({
        excel_path: uploadResult.file_path,
        event_name: eventName || undefined,
        city: city || undefined,
        country: country || undefined,
        start_date: startDate || undefined,
        end_date: endDate || undefined,
        event_type: eventType,
      });
      setRunResult(
        `Pipeline complete — Decision: ${result.decision.toUpperCase()} | Score: ${result.profitability_score.toFixed(1)} | Hotels cheaper: ${result.hotels_cheaper_count}`
      );
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Pipeline failed";
      setRunResult(`Error: ${msg}`);
    } finally {
      setRunning(false);
    }
  }

  return (
    <div className="p-8 max-w-2xl">
      <h1 className="text-xl font-semibold text-[#f5f5f5] mb-2">Upload Excel</h1>
      <p className="text-sm text-[#555] mb-6">
        Upload a vendor/competitor pricing sheet, fill in event details, then trigger the full pipeline.
      </p>

      <UploadDropzone onUpload={setUploadResult} />

      {uploadResult && (
        <div className="mt-8 space-y-4">
          <h2 className="text-sm font-semibold text-[#f5f5f5]">Event Details</h2>
          <div className="grid grid-cols-2 gap-3">
            <div className="col-span-2">
              <label className="block text-xs text-[#888] mb-1">Event Name</label>
              <input
                value={eventName}
                onChange={(e) => setEventName(e.target.value)}
                placeholder="Arab Health 2025"
                className="w-full px-3 py-2 bg-[#111] border border-[#222] rounded-md text-sm text-[#f5f5f5] placeholder-[#444] focus:outline-none focus:border-[#3b82f6]"
              />
            </div>
            <div>
              <label className="block text-xs text-[#888] mb-1">City</label>
              <input
                value={city}
                onChange={(e) => setCity(e.target.value)}
                placeholder="Dubai"
                className="w-full px-3 py-2 bg-[#111] border border-[#222] rounded-md text-sm text-[#f5f5f5] placeholder-[#444] focus:outline-none focus:border-[#3b82f6]"
              />
            </div>
            <div>
              <label className="block text-xs text-[#888] mb-1">Country</label>
              <input
                value={country}
                onChange={(e) => setCountry(e.target.value)}
                placeholder="UAE"
                className="w-full px-3 py-2 bg-[#111] border border-[#222] rounded-md text-sm text-[#f5f5f5] placeholder-[#444] focus:outline-none focus:border-[#3b82f6]"
              />
            </div>
            <div>
              <label className="block text-xs text-[#888] mb-1">Start Date</label>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="w-full px-3 py-2 bg-[#111] border border-[#222] rounded-md text-sm text-[#f5f5f5] focus:outline-none focus:border-[#3b82f6]"
              />
            </div>
            <div>
              <label className="block text-xs text-[#888] mb-1">End Date</label>
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="w-full px-3 py-2 bg-[#111] border border-[#222] rounded-md text-sm text-[#f5f5f5] focus:outline-none focus:border-[#3b82f6]"
              />
            </div>
            <div>
              <label className="block text-xs text-[#888] mb-1">Event Type</label>
              <select
                value={eventType}
                onChange={(e) => setEventType(e.target.value)}
                className="w-full px-3 py-2 bg-[#111] border border-[#222] rounded-md text-sm text-[#f5f5f5] focus:outline-none focus:border-[#3b82f6]"
              >
                {["medical", "pharma", "health", "tech", "industrial", "business"].map((t) => (
                  <option key={t} value={t} className="bg-[#111]">{t}</option>
                ))}
              </select>
            </div>
          </div>

          <button
            onClick={handleRun}
            disabled={running}
            className="w-full py-2.5 bg-[#3b82f6] text-white font-medium text-sm rounded-md hover:bg-blue-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {running ? "Running pipeline…" : "Run Pipeline"}
          </button>

          {runResult && (
            <div className={`p-3 rounded-lg text-sm border ${runResult.startsWith("Error") ? "bg-red-900/20 border-red-500/30 text-red-400" : "bg-green-900/20 border-green-500/30 text-green-400"}`}>
              {runResult}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
