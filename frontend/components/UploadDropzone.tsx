"use client";
import { useState, useRef, DragEvent } from "react";
import { api } from "@/lib/api";
import type { ExcelUploadResponse } from "@/lib/types";

interface UploadDropzoneProps {
  onUpload?: (result: ExcelUploadResponse) => void;
}

export default function UploadDropzone({ onUpload }: UploadDropzoneProps) {
  const [dragging, setDragging] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ExcelUploadResponse | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  async function handleFile(file: File) {
    setLoading(true);
    setError(null);
    try {
      const data = await api.uploadExcel(file);
      setResult(data);
      onUpload?.(data);
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Upload failed";
      setError(msg);
    } finally {
      setLoading(false);
    }
  }

  function onDrop(e: DragEvent<HTMLDivElement>) {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files?.[0];
    if (file) handleFile(file);
  }

  return (
    <div className="space-y-4">
      <div
        className={`border-2 border-dashed rounded-xl p-10 flex flex-col items-center justify-center cursor-pointer transition-colors ${
          dragging ? "border-[#3b82f6] bg-blue-500/5" : "border-[#2a2a2a] bg-[#0d0d0d] hover:border-[#333]"
        }`}
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
        onClick={() => fileRef.current?.click()}
      >
        <input
          ref={fileRef}
          type="file"
          accept=".xlsx,.xls,.csv"
          className="hidden"
          onChange={(e) => { const f = e.target.files?.[0]; if (f) handleFile(f); }}
        />
        <div className="text-4xl mb-3">📊</div>
        <p className="text-[#f5f5f5] font-medium">Drop your Excel/CSV file here</p>
        <p className="text-[#555] text-sm mt-1">.xlsx, .xls, or .csv — Vendor + Competitor sheets</p>
        {loading && <p className="text-[#3b82f6] text-sm mt-3 animate-pulse">Uploading & parsing…</p>}
      </div>

      {error && (
        <div className="bg-red-900/20 border border-red-500/30 rounded-lg p-3 text-red-400 text-sm">{error}</div>
      )}

      {result && (
        <div className="bg-green-900/20 border border-green-500/30 rounded-lg p-4 space-y-3">
          <p className="text-green-400 text-sm font-medium">
            Parsed {result.vendor_rows} vendor rows, {result.competitor_rows} competitor rows
          </p>
          {result.preview.length > 0 && (
            <div className="overflow-x-auto rounded border border-[#222]">
              <table className="text-xs w-full">
                <thead>
                  <tr className="bg-[#111] border-b border-[#222]">
                    {Object.keys(result.preview[0]).map((col) => (
                      <th key={col} className="px-3 py-2 text-left text-[#888] capitalize">{col}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {result.preview.map((row, i) => (
                    <tr key={i} className="border-b border-[#1a1a1a]">
                      {Object.values(row).map((val, j) => (
                        <td key={j} className="px-3 py-2 text-[#aaa]">{String(val ?? "")}</td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
