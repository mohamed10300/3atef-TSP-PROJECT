"""
Generates a structured report from final pipeline state.
Saves to DB and produces a PDF.
"""
import asyncio
import uuid
from datetime import datetime

from backend.core.state import AgentState, ReportData
from backend.utils.pdf_generator import generate_pdf
from backend.utils.logger import get_logger

logger = get_logger(__name__)


def _build_report_content(state: AgentState) -> dict:
    event = state.get("event") or {}
    hotels = state.get("hotels", [])
    approval = state.get("approval") or {}
    scores = state.get("scores") or {}

    start = event.get("start_date", "")
    end = event.get("end_date", "")
    dates = f"{start} → {end}" if start and end else ""

    return {
        "event_id": event.get("id", ""),
        "event_name": event.get("name", ""),
        "event_type": event.get("type", ""),
        "location": f"{event.get('city', '')}, {event.get('country', '')}",
        "venue_name": event.get("venue_name", ""),
        "dates": dates,
        "decision": approval.get("decision", "pending"),
        "hotels_cheaper_count": approval.get("hotels_cheaper_count", 0),
        "min_price_difference": approval.get("min_price_difference", 0.0),
        "rule_triggered": approval.get("rule_triggered", ""),
        "profitability_score": scores.get("profitability_score", 0.0),
        "risk_score": scores.get("risk_score", 0),
        "risk_breakdown": scores.get("risk_breakdown", {}),
        "hotels": [
            {
                "name": h["name"],
                "market_price": h["market_price"],
                "vendor_price": h["vendor_price"],
                "competitor_price": h["competitor_price"],
                "price_difference": h["price_difference"],
                "availability": h["availability"],
                "rating": h["rating"],
                "refund_policy": h.get("refund_policy", ""),
                "cancellation_penalty": h.get("cancellation_penalty", ""),
                "no_show_policy": h.get("no_show_policy", ""),
            }
            for h in hotels
        ],
        "generated_at": datetime.utcnow().isoformat(),
    }


async def reporting_agent(state: AgentState) -> AgentState:
    event = state.get("event")
    if not event:
        logger.warning("reporting_agent: no event in state")
        return {**state, "step": "reporting_agent_skipped"}

    content = _build_report_content(state)
    approval = state.get("approval") or {}
    decision = approval.get("decision", "pending")
    report_type = "approved_events" if decision == "approved" else "rejected_events"

    report_id = str(uuid.uuid4())
    pdf_filename = f"report_{report_id[:8]}.pdf"

    try:
        pdf_path = generate_pdf(content, filename=pdf_filename)
    except Exception as e:
        logger.error(f"reporting_agent: PDF generation failed: {e}")
        pdf_path = ""

    report: ReportData = ReportData(
        event_id=event["id"],
        report_type=report_type,
        content=content,
        pdf_url=pdf_path,
    )

    logger.info(f"reporting_agent: report generated — type={report_type}, pdf={pdf_path}")
    return {**state, "report": report, "step": "reporting_agent_done"}


if __name__ == "__main__":
    state: AgentState = {
        "raw_event_input": None,
        "excel_path": None,
        "email_content": None,
        "event": {
            "id": "evt-001", "name": "Dubai Medical Expo", "type": "medical",
            "country": "UAE", "city": "Dubai", "venue_name": "DWTC",
            "venue_address": "Trade Centre", "start_date": "2025-03-10",
            "end_date": "2025-03-14", "source": "manual",
        },
        "hotels": [
            {
                "id": "h1", "event_id": "evt-001", "name": "Hotel A", "address": "",
                "distance_from_venue_km": 0.5, "rating": 4.2, "room_type": "Standard",
                "market_price": 90.0, "vendor_price": 100.0, "competitor_price": 95.0,
                "price_difference": -10.0, "is_cheaper_than_vendor": True,
                "refund_policy": "Free cancellation", "cancellation_penalty": "None",
                "no_show_policy": "1 night charge", "availability": True, "booking_url": "",
            },
        ],
        "vendor_prices": {}, "competitor_prices": {},
        "approval": {"decision": "approved", "hotels_cheaper_count": 3, "min_price_difference": -10.0, "rule_triggered": "3_hotels_4_dollar_rule", "decided_by": "system"},
        "scores": {"profitability_score": 74.5, "risk_score": 0, "risk_breakdown": {}},
        "report": None, "error": None, "step": "scoring_done",
    }

    result = asyncio.run(reporting_agent(state))
    print("Report:", result.get("report"))
