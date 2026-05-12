"""
Risk score: additive — higher = more risky.
Profitability score: 0-100.
"""
from typing import List

from backend.core.state import HotelData, ScoreResult

# --- Risk scoring constants ---
RISK_RULES: list[tuple[str, int]] = [
    ("NO REFUND", 30),
    ("NON-REFUNDABLE", 30),
    ("100% PENALTY", 25),
    ("NO MODIFICATIONS", 20),
    ("NO DATE CHANGE", 15),
]
RISK_UNAVAILABLE = 20

# Event type profitability weight
EVENT_TYPE_WEIGHT: dict[str, float] = {
    "medical": 1.3,
    "pharma": 1.3,
    "health": 1.2,
    "tech": 1.1,
    "industrial": 1.0,
    "business": 1.0,
}


def _policy_risk(hotel: HotelData) -> tuple[int, dict[str, int]]:
    breakdown: dict[str, int] = {}
    total = 0

    policies = " ".join([
        hotel.get("refund_policy") or "",
        hotel.get("cancellation_penalty") or "",
        hotel.get("no_show_policy") or "",
    ]).upper()

    for keyword, points in RISK_RULES:
        if keyword in policies:
            breakdown[keyword] = points
            total += points

    if not hotel.get("availability", True):
        breakdown["UNAVAILABLE"] = RISK_UNAVAILABLE
        total += RISK_UNAVAILABLE

    return total, breakdown


def calculate_scores(hotels: List[HotelData], event_type: str = "business") -> ScoreResult:
    if not hotels:
        return ScoreResult(profitability_score=0.0, risk_score=0, risk_breakdown={})

    # --- Risk score (worst hotel = representative risk) ---
    max_risk = 0
    combined_breakdown: dict[str, int] = {}
    for hotel in hotels:
        risk, breakdown = _policy_risk(hotel)
        if risk > max_risk:
            max_risk = risk
            combined_breakdown = breakdown

    # --- Profitability score ---
    diffs = [h["price_difference"] for h in hotels]
    avg_diff = sum(diffs) / len(diffs)     # negative = market cheaper than vendor
    available_count = sum(1 for h in hotels if h.get("availability", True))
    availability_ratio = available_count / len(hotels)

    # Normalize avg_diff: clamp to [-50, 0] → [100, 0]
    # If avg market is $50+ cheaper: max profitability
    clamped = max(-50.0, min(0.0, avg_diff))
    diff_score = (abs(clamped) / 50.0) * 70   # up to 70 points from price gap

    avail_score = availability_ratio * 15      # up to 15 points
    policy_score = max(0.0, (1 - max_risk / 120) * 15)  # up to 15 points

    raw_score = diff_score + avail_score + policy_score
    weight = EVENT_TYPE_WEIGHT.get(event_type.lower(), 1.0)
    profitability = min(100.0, round(raw_score * weight, 2))

    return ScoreResult(
        profitability_score=profitability,
        risk_score=max_risk,
        risk_breakdown=combined_breakdown,
    )


if __name__ == "__main__":
    from backend.core.approval_engine import sample_hotels  # type: ignore
    result = calculate_scores(sample_hotels, event_type="medical")  # type: ignore
    print(result)
