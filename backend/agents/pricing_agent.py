"""
Computes final price comparisons: market vs vendor vs competitor.
Updates hotel price_difference and is_cheaper_than_vendor for all hotels in state.
"""
from backend.core.state import AgentState, HotelData
from backend.utils.logger import get_logger

logger = get_logger(__name__)


def _enrich_hotel(hotel: HotelData) -> HotelData:
    market = hotel["market_price"]
    vendor = hotel["vendor_price"]

    diff = round(market - vendor, 2)
    cheaper = diff <= -4.0

    return {
        **hotel,
        "price_difference": diff,
        "is_cheaper_than_vendor": cheaper,
        "availability": market > 0,
    }


async def pricing_agent(state: AgentState) -> AgentState:
    hotels = state.get("hotels", [])

    if not hotels:
        logger.info("pricing_agent: no hotels to process")
        return {**state, "step": "pricing_agent_skipped"}

    vendor_prices: dict[str, float] = {k: v["vendor_price"] for k, v in state.get("vendor_prices", {}).items()}
    competitor_prices: dict[str, float] = state.get("competitor_prices", {})

    enriched: list[HotelData] = []
    for hotel in hotels:
        name = hotel["name"]

        # Patch in vendor/competitor if hotel was built without them
        if hotel["vendor_price"] == 0.0:
            vendor = vendor_prices.get(name) or next(
                (v for k, v in vendor_prices.items() if k.lower() == name.lower()), 0.0
            )
            hotel = {**hotel, "vendor_price": round(vendor, 2)}

        if hotel["competitor_price"] == 0.0:
            comp = competitor_prices.get(name) or next(
                (v for k, v in competitor_prices.items() if k.lower() == name.lower()), 0.0
            )
            hotel = {**hotel, "competitor_price": round(comp, 2)}

        enriched.append(_enrich_hotel(hotel))

    cheaper_count = sum(1 for h in enriched if h["is_cheaper_than_vendor"])
    logger.info(f"pricing_agent: {cheaper_count}/{len(enriched)} hotels cheaper than vendor by >= $4")

    return {**state, "hotels": enriched, "step": "pricing_agent_done"}


if __name__ == "__main__":
    import asyncio
    from backend.core.state import HotelData

    sample: list[HotelData] = [
        {
            "id": "1", "event_id": "e1", "name": "Hotel A", "address": "",
            "distance_from_venue_km": 0.5, "rating": 4.0, "room_type": "Standard",
            "market_price": 88.00, "vendor_price": 100.00, "competitor_price": 95.00,
            "price_difference": 0.0, "is_cheaper_than_vendor": False,
            "refund_policy": "", "cancellation_penalty": "", "no_show_policy": "",
            "availability": True, "booking_url": "",
        },
    ]

    state: AgentState = {
        "raw_event_input": None, "excel_path": None, "email_content": None,
        "event": None, "hotels": sample,
        "vendor_prices": {"Hotel A": {"vendor_price": 100.0, "room_type": "Standard"}},
        "competitor_prices": {"Hotel A": 95.0},
        "approval": None, "scores": None, "report": None, "error": None, "step": "start",
    }

    result = asyncio.run(pricing_agent(state))
    for h in result["hotels"]:
        print(f"{h['name']}: market={h['market_price']} vendor={h['vendor_price']} diff={h['price_difference']} cheaper={h['is_cheaper_than_vendor']}")
