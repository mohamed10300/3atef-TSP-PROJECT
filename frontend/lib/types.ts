export interface Event {
  id: string;
  name: string;
  type: string;
  country: string;
  city: string;
  venue_name: string;
  venue_address: string;
  start_date: string;
  end_date: string;
  source: string;
  status: "pending" | "approved" | "rejected";
  score: number;
  risk_score: number;
  created_at: string;
  hotels?: Hotel[];
  decisions?: ApprovalDecision[];
}

export interface Hotel {
  id: string;
  event_id: string;
  name: string;
  address: string;
  distance_from_venue_km: number;
  rating: number;
  room_type: string;
  market_price: number;
  vendor_price: number;
  competitor_price: number;
  price_difference: number;
  is_cheaper_than_vendor: boolean;
  refund_policy: string;
  cancellation_penalty: string;
  no_show_policy: string;
  availability: boolean;
  booking_url: string;
  collected_at?: string;
}

export interface ApprovalDecision {
  decision: "approved" | "rejected";
  hotels_cheaper_count: number;
  min_price_difference: number;
  rule_triggered: string;
  decided_at: string;
  decided_by: string;
}

export interface Report {
  id: string;
  event_id: string;
  report_type: string;
  content: Record<string, unknown>;
  pdf_url: string;
  generated_at: string;
}

export interface RunRequest {
  raw_event_input?: string;
  excel_path?: string;
  email_content?: string;
  event_name?: string;
  event_type?: string;
  country?: string;
  city?: string;
  venue_name?: string;
  venue_address?: string;
  start_date?: string;
  end_date?: string;
}

export interface RunResponse {
  event_id: string;
  decision: string;
  profitability_score: number;
  risk_score: number;
  hotels_cheaper_count: number;
  pdf_url: string;
  step: string;
}

export interface ExcelUploadResponse {
  file_path: string;
  vendor_rows: number;
  competitor_rows: number;
  preview: Record<string, unknown>[];
  vendor_prices: Record<string, { vendor_price: number; room_type: string }>;
  competitor_prices: Record<string, number>;
}
