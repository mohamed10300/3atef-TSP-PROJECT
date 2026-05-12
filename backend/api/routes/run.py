"""POST /api/run — trigger full pipeline for a new event input."""
import uuid
from typing import Optional

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

from backend.core.graph import run_pipeline
from backend.core.state import AgentState
from backend.db.database import db_session
from backend.db.models import Event, Hotel, ApprovalDecision, Report
from backend.utils.logger import get_logger

router = APIRouter(prefix="/api/run", tags=["run"])
logger = get_logger(__name__)


class RunRequest(BaseModel):
    raw_event_input: Optional[str] = None
    excel_path: Optional[str] = None
    email_content: Optional[str] = None
    event_name: Optional[str] = None
    event_type: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    venue_name: Optional[str] = None
    venue_address: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class RunResponse(BaseModel):
    event_id: str
    decision: str
    profitability_score: float
    risk_score: int
    hotels_cheaper_count: int
    pdf_url: str
    step: str


def _persist_results(state: AgentState) -> None:
    """Save pipeline results to DB."""
    event_data = state.get("event")
    if not event_data:
        return

    with db_session() as db:
        # Upsert Event
        event = db.query(Event).filter(Event.id == event_data["id"]).first()
        if not event:
            event = Event(id=event_data["id"])
            db.add(event)

        event.name = event_data.get("name", "")
        event.type = event_data.get("type", "business")
        event.country = event_data.get("country", "")
        event.city = event_data.get("city", "")
        event.venue_name = event_data.get("venue_name", "")
        event.venue_address = event_data.get("venue_address", "")
        event.start_date = event_data.get("start_date") or None
        event.end_date = event_data.get("end_date") or None
        event.source = event_data.get("source", "manual")

        approval = state.get("approval")
        scores = state.get("scores")
        if approval:
            event.status = approval.get("decision", "pending")
        if scores:
            event.score = scores.get("profitability_score", 0.0)
            event.risk_score = scores.get("risk_score", 0)

        db.flush()

        # Insert Hotels
        for h in state.get("hotels", []):
            existing = db.query(Hotel).filter(Hotel.id == h["id"]).first()
            if not existing:
                hotel = Hotel(
                    id=h["id"],
                    event_id=event.id,
                    name=h["name"],
                    address=h.get("address", ""),
                    distance_from_venue_km=h.get("distance_from_venue_km", 0.0),
                    rating=h.get("rating", 0.0),
                    room_type=h.get("room_type", ""),
                    market_price=h.get("market_price", 0.0),
                    vendor_price=h.get("vendor_price", 0.0),
                    competitor_price=h.get("competitor_price", 0.0),
                    price_difference=h.get("price_difference", 0.0),
                    is_cheaper_than_vendor=h.get("is_cheaper_than_vendor", False),
                    refund_policy=h.get("refund_policy", ""),
                    cancellation_penalty=h.get("cancellation_penalty", ""),
                    no_show_policy=h.get("no_show_policy", ""),
                    availability=h.get("availability", True),
                    booking_url=h.get("booking_url", ""),
                )
                db.add(hotel)

        # Approval decision
        if approval:
            decision_record = ApprovalDecision(
                id=str(uuid.uuid4()),
                event_id=event.id,
                decision=approval.get("decision", "pending"),
                hotels_cheaper_count=approval.get("hotels_cheaper_count", 0),
                min_price_difference=approval.get("min_price_difference", 0.0),
                rule_triggered=approval.get("rule_triggered", ""),
                decided_by=approval.get("decided_by", "system"),
            )
            db.add(decision_record)

        # Report
        report = state.get("report")
        if report:
            report_record = Report(
                id=str(uuid.uuid4()),
                event_id=event.id,
                report_type=report.get("report_type", ""),
                content=report.get("content", {}),
                pdf_url=report.get("pdf_url", ""),
            )
            db.add(report_record)


@router.post("", response_model=RunResponse)
async def trigger_pipeline(req: RunRequest, background_tasks: BackgroundTasks):
    event_data = None
    if req.event_name:
        event_data = {
            "id": str(uuid.uuid4()),
            "name": req.event_name,
            "type": req.event_type or "business",
            "country": req.country or "",
            "city": req.city or "",
            "venue_name": req.venue_name or "",
            "venue_address": req.venue_address or "",
            "start_date": req.start_date or "",
            "end_date": req.end_date or "",
            "source": "manual",
        }

    initial: AgentState = {
        "raw_event_input": req.raw_event_input,
        "excel_path": req.excel_path,
        "email_content": req.email_content,
        "event": event_data,
        "hotels": [],
        "vendor_prices": {},
        "competitor_prices": {},
        "approval": None,
        "scores": None,
        "report": None,
        "error": None,
        "step": "start",
    }

    try:
        final = await run_pipeline(initial)
    except Exception as e:
        logger.error(f"Pipeline error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    if final.get("error"):
        raise HTTPException(status_code=422, detail=final["error"])

    background_tasks.add_task(_persist_results, final)

    approval = final.get("approval") or {}
    scores = final.get("scores") or {}
    report = final.get("report") or {}
    event = final.get("event") or {}

    return RunResponse(
        event_id=event.get("id", ""),
        decision=approval.get("decision", "pending"),
        profitability_score=scores.get("profitability_score", 0.0),
        risk_score=scores.get("risk_score", 0),
        hotels_cheaper_count=approval.get("hotels_cheaper_count", 0),
        pdf_url=report.get("pdf_url", ""),
        step=final.get("step", ""),
    )
