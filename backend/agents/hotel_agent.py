"""
Scrapes hotel prices near the event venue for the event dates.
Merges results from Booking.com, Expedia, and Agoda.
Enriches each hotel with vendor_price and competitor_price from state.
"""
import asyncio
import uuid
from datetime import date
from typing import Optional

from backend.core.state import AgentState, HotelData
from backend.scrapers.booking_scraper import scrape_booking
from backend.scrapers.expedia_scraper import scrape_expedia
from backend.scrapers.agoda_scraper import scrape_agoda
from backend.config import settings
from backend.utils.logger import get_logger

logger = get_logger(__name__)


def _parse_date(s: str) -> Optional[date]:
    try:
        return date.fromisoformat(s)
    except Exception:
        return None


def _merge_scraped(booking: list[dict], expedia: list[dict], agoda: list[dict]) -> list[dict]:
    """Deduplicate by name (case-insensitive), keep lowest market_price per hotel."""
    merged: dict[str, dict] = {}
    for hotel in booking + expedia + agoda:
        key = hotel["name"].lower().strip()
        if key not in merged or hotel["market_price"] < merged[key]["market_price"]:
            merged[key] = hotel
    return list(merged.values())


def _build_hotel_data(
    raw: dict,
    event_id: str,
    vendor_prices: dict[str, float],
    competitor_prices: dict[str, float],
    room_types: dict[str, str],
) -> HotelData:
    name = raw["name"]
    market_price = round(raw.get("market_price", 0.0), 2)

    # Try exact match, then case-insensitive
    vendor_price = vendor_prices.get(name) or next(
        (v for k, v in vendor_prices.items() if k.lower() == name.lower()), 0.0
    )
    competitor_price = competitor_prices.get(name) or next(
        (v for k, v in competitor_prices.items() if k.lower() == name.lower()), 0.0
    )
    room_type = room_types.get(name) or next(
        (v for k, v in room_types.items() if k.lower() == name.lower()), ""
    )

    price_diff = round(market_price - vendor_price, 2)

    return HotelData(
        id=str(uuid.uuid4()),
        event_id=event_id,
        name=name,
        address="",
        distance_from_venue_km=0.0,
        rating=round(raw.get("rating", 0.0), 1),
        room_type=room_type,
        market_price=market_price,
        vendor_price=round(vendor_price, 2),
        competitor_price=round(competitor_price, 2),
        price_difference=price_diff,
        is_cheaper_than_vendor=price_diff <= -4.0,
        refund_policy="",
        cancellation_penalty="",
        no_show_policy="",
        availability=market_price > 0,
        booking_url=raw.get("booking_url", ""),
    )


async def hotel_agent(state: AgentState) -> AgentState:
    event = state.get("event")
    if not event:
        logger.warning("hotel_agent: no event in state, skipping")
        return {**state, "step": "hotel_agent_skipped"}

    location = f"{event['city']}, {event['country']}"
    check_in = _parse_date(event.get("start_date", ""))
    check_out = _parse_date(event.get("end_date", ""))

    if not check_in or not check_out:
        logger.error("hotel_agent: invalid event dates")
        return {**state, "error": "Invalid event dates", "step": "hotel_agent_error"}

    headless = settings.SCRAPER_HEADLESS
    logger.info(f"hotel_agent: scraping hotels in {location} from {check_in} to {check_out}")

    booking, expedia, agoda = await asyncio.gather(
        scrape_booking(location, check_in, check_out, headless=headless),
        scrape_expedia(location, check_in, check_out, headless=headless),
        scrape_agoda(location, check_in, check_out, headless=headless),
        return_exceptions=True,
    )

    booking = booking if isinstance(booking, list) else []
    expedia = expedia if isinstance(expedia, list) else []
    agoda = agoda if isinstance(agoda, list) else []

    merged = _merge_scraped(booking, expedia, agoda)

    vendor_prices: dict[str, float] = {k: v["vendor_price"] for k, v in state.get("vendor_prices", {}).items()}
    room_types: dict[str, str] = {k: v.get("room_type", "") for k, v in state.get("vendor_prices", {}).items()}
    competitor_prices: dict[str, float] = state.get("competitor_prices", {})

    hotels: list[HotelData] = [
        _build_hotel_data(raw, event["id"], vendor_prices, competitor_prices, room_types)
        for raw in merged
    ]

    logger.info(f"hotel_agent: built {len(hotels)} hotel records")
    return {**state, "hotels": hotels, "step": "hotel_agent_done"}


if __name__ == "__main__":
    state: AgentState = {
        "raw_event_input": None,
        "excel_path": None,
        "email_content": None,
        "event": {
            "id": "test-event-1",
            "name": "Dubai Medical Expo 2025",
            "type": "medical",
            "country": "UAE",
            "city": "Dubai",
            "venue_name": "Dubai World Trade Centre",
            "venue_address": "Trade Centre 1, Dubai",
            "start_date": "2025-03-10",
            "end_date": "2025-03-14",
            "source": "manual",
        },
        "hotels": [],
        "vendor_prices": {},
        "competitor_prices": {},
        "approval": None,
        "scores": None,
        "report": None,
        "error": None,
        "step": "start",
    }
    result = asyncio.run(hotel_agent(state))
    print(f"Hotels found: {len(result.get('hotels', []))}")
    for h in result.get("hotels", [])[:3]:
        print(h)
