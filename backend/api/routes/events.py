"""GET/PUT /api/events — event CRUD."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.db.database import get_db
from backend.db.models import Event

router = APIRouter(prefix="/api/events", tags=["events"])


class EventOut(BaseModel):
    id: str
    name: str
    type: str
    country: str
    city: str
    venue_name: Optional[str]
    venue_address: Optional[str]
    start_date: Optional[str]
    end_date: Optional[str]
    source: str
    status: str
    score: float
    risk_score: int
    created_at: str

    model_config = {"from_attributes": True}


def _serialize(event: Event) -> dict:
    return {
        "id": event.id,
        "name": event.name,
        "type": event.type,
        "country": event.country,
        "city": event.city,
        "venue_name": event.venue_name or "",
        "venue_address": event.venue_address or "",
        "start_date": str(event.start_date) if event.start_date else "",
        "end_date": str(event.end_date) if event.end_date else "",
        "source": event.source,
        "status": event.status,
        "score": event.score or 0.0,
        "risk_score": event.risk_score or 0,
        "created_at": str(event.created_at),
    }


@router.get("")
async def list_events(
    status: Optional[str] = Query(None),
    event_type: Optional[str] = Query(None, alias="type"),
    db: Session = Depends(get_db),
):
    q = db.query(Event)
    if status:
        q = q.filter(Event.status == status)
    if event_type:
        q = q.filter(Event.type == event_type)
    events = q.order_by(Event.created_at.desc()).all()
    return [_serialize(e) for e in events]


@router.get("/{event_id}")
async def get_event(event_id: str, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    data = _serialize(event)
    data["hotels"] = [
        {
            "id": h.id,
            "name": h.name,
            "address": h.address or "",
            "distance_from_venue_km": h.distance_from_venue_km,
            "rating": h.rating,
            "room_type": h.room_type or "",
            "market_price": h.market_price,
            "vendor_price": h.vendor_price,
            "competitor_price": h.competitor_price,
            "price_difference": h.price_difference,
            "is_cheaper_than_vendor": h.is_cheaper_than_vendor,
            "refund_policy": h.refund_policy or "",
            "cancellation_penalty": h.cancellation_penalty or "",
            "no_show_policy": h.no_show_policy or "",
            "availability": h.availability,
            "booking_url": h.booking_url or "",
        }
        for h in event.hotels
    ]
    data["decisions"] = [
        {
            "decision": d.decision,
            "hotels_cheaper_count": d.hotels_cheaper_count,
            "min_price_difference": d.min_price_difference,
            "rule_triggered": d.rule_triggered,
            "decided_at": str(d.decided_at),
            "decided_by": d.decided_by,
        }
        for d in event.decisions
    ]
    return data


@router.get("/{event_id}/report")
async def get_event_report(event_id: str, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    if not event.reports:
        raise HTTPException(status_code=404, detail="No report found for this event")
    report = event.reports[-1]
    return {
        "id": report.id,
        "event_id": report.event_id,
        "report_type": report.report_type,
        "content": report.content,
        "pdf_url": report.pdf_url,
        "generated_at": str(report.generated_at),
    }
