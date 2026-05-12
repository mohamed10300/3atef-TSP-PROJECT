"""GET /api/hotels — hotels for a specific event."""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.db.database import get_db
from backend.db.models import Hotel

router = APIRouter(prefix="/api/hotels", tags=["hotels"])


@router.get("")
async def list_hotels(
    event_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    q = db.query(Hotel)
    if event_id:
        q = q.filter(Hotel.event_id == event_id)
    hotels = q.all()
    return [
        {
            "id": h.id,
            "event_id": h.event_id,
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
            "collected_at": str(h.collected_at),
        }
        for h in hotels
    ]
