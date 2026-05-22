import axios from "axios";
import type {
  Event,
  Hotel,
  Report,
  RunRequest,
  RunResponse,
  ExcelUploadResponse,
} from "./types";

const BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const http = axios.create({
  baseURL: BASE,
  headers: {
    "ngrok-skip-browser-warning": "true",
  },
});

export const api = {
  async runPipeline(req: RunRequest): Promise<RunResponse> {
    const { data } = await http.post<RunResponse>("/api/run", req);
    return data;
  },

  async listEvents(params?: { status?: string; type?: string }): Promise<Event[]> {
    const { data } = await http.get<Event[]>("/api/events", { params });
    return data;
  },

  async getEvent(id: string): Promise<Event> {
    const { data } = await http.get<Event>(`/api/events/${id}`);
    return data;
  },

  async getEventReport(id: string): Promise<Report> {
    const { data } = await http.get<Report>(`/api/events/${id}/report`);
    return data;
  },

  async listHotels(eventId?: string): Promise<Hotel[]> {
    const { data } = await http.get<Hotel[]>("/api/hotels", {
      params: eventId ? { event_id: eventId } : {},
    });
    return data;
  },

  async listReports(): Promise<Report[]> {
    const { data } = await http.get<Report[]>("/api/reports");
    return data;
  },

  getReportExportUrl(reportId: string): string {
    return `${BASE}/api/reports/${reportId}/export`;
  },

  async uploadExcel(file: File): Promise<ExcelUploadResponse> {
    const form = new FormData();
    form.append("file", file);
    const { data } = await http.post<ExcelUploadResponse>("/api/excel/upload", form, {
      headers: {
        "Content-Type": "multipart/form-data",
        "ngrok-skip-browser-warning": "true",
      },
    });
    return data;
  },
};