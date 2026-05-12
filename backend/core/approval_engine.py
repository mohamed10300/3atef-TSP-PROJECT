"""
Approval rule:
  If >= 3 hotels have market_price cheaper than vendor_price by >= $4.00 → APPROVED
  Otherwise → REJECTED

  price_difference = market_price - vendor_price
  qualifies when price_difference <= -4.0  (market is cheaper by at least $4)
"""
from datetime import datetime
from typing import List

from backend.core.state import HotelData, ApprovalResult


CHEAPER_BY_THRESHOLD = -4.0   # market must be at least $4 cheaper than vendor
MIN_QUALIFYING_HOTELS = 3
RULE_NAME = "3_hotels_4_dollar_rule"


def run_approval(hotels: List[HotelData]) -> ApprovalResult:
    qualifying = [h for h in hotels if h["price_difference"] <= CHEAPER_BY_THRESHOLD]
    count = len(qualifying)

    min_diff = min((h["price_difference"] for h in qualifying), default=0.0)

    decision = "approved" if count >= MIN_QUALIFYING_HOTELS else "rejected"

    return ApprovalResult(
        decision=decision,
        hotels_cheaper_count=count,
        min_price_difference=round(min_diff, 2),
        rule_triggered=RULE_NAME,
        decided_by="system",
    )


if __name__ == "__main__":
    sample_hotels: List[HotelData] = [
        {
            "id": "1", "event_id": "e1", "name": "Hotel A", "address": "", "distance_from_venue_km": 0.5,
            "rating": 4.2, "room_type": "Standard", "market_price": 90.00, "vendor_price": 100.00,
            "competitor_price": 95.00, "price_difference": -10.00, "is_cheaper_than_vendor": True,
            "refund_policy": "Free cancellation", "cancellation_penalty": "None", "no_show_policy": "1 night",
            "availability": True, "booking_url": "",
        },
        {
            "id": "2", "event_id": "e1", "name": "Hotel B", "address": "", "distance_from_venue_km": 1.0,
            "rating": 3.8, "room_type": "Standard", "market_price": 88.00, "vendor_price": 100.00,
            "competitor_price": 92.00, "price_difference": -12.00, "is_cheaper_than_vendor": True,
            "refund_policy": "Non-refundable", "cancellation_penalty": "100% PENALTY", "no_show_policy": "NO REFUND",
            "availability": True, "booking_url": "",
        },
        {
            "id": "3", "event_id": "e1", "name": "Hotel C", "address": "", "distance_from_venue_km": 1.5,
            "rating": 4.0, "room_type": "Deluxe", "market_price": 94.00, "vendor_price": 100.00,
            "competitor_price": 98.00, "price_difference": -6.00, "is_cheaper_than_vendor": True,
            "refund_policy": "Free cancellation", "cancellation_penalty": "None", "no_show_policy": "1 night",
            "availability": True, "booking_url": "",
        },
    ]
    result = run_approval(sample_hotels)
    print(result)
