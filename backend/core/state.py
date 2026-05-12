from typing import TypedDict, Optional
from datetime import date


class EventData(TypedDict):
    id: str
    name: str
    type: str
    country: str
    city: str
    venue_name: str
    venue_address: str
    start_date: str  # ISO format
    end_date: str    # ISO format
    source: str


class HotelData(TypedDict):
    id: str
    event_id: str
    name: str
    address: str
    distance_from_venue_km: float
    rating: float
    room_type: str
    market_price: float
    vendor_price: float
    competitor_price: float
    price_difference: float
    is_cheaper_than_vendor: bool
    refund_policy: str
    cancellation_penalty: str
    no_show_policy: str
    availability: bool
    booking_url: str


class ApprovalResult(TypedDict):
    decision: str          # "approved" | "rejected"
    hotels_cheaper_count: int
    min_price_difference: float
    rule_triggered: str
    decided_by: str


class ScoreResult(TypedDict):
    profitability_score: float   # 0–100
    risk_score: int              # additive points
    risk_breakdown: dict[str, int]


class ReportData(TypedDict):
    event_id: str
    report_type: str
    content: dict
    pdf_url: str


class AgentState(TypedDict):
    # Input
    raw_event_input: Optional[str]
    excel_path: Optional[str]
    email_content: Optional[str]

    # Extracted data
    event: Optional[EventData]
    hotels: list[HotelData]
    vendor_prices: dict[str, float]    # hotel_name → vendor_price
    competitor_prices: dict[str, float]  # hotel_name → competitor_price

    # Pipeline outputs
    approval: Optional[ApprovalResult]
    scores: Optional[ScoreResult]
    report: Optional[ReportData]

    # Control
    error: Optional[str]
    step: str  # current pipeline step name
