"""
Extracts/validates full venue data from the event — address, GPS coords if available.
Uses GPT-4o to normalize venue info from web content.
"""
import asyncio
import json
from typing import Optional

from openai import AsyncOpenAI

from backend.core.state import AgentState, EventData
from backend.config import settings
from backend.utils.logger import get_logger

logger = get_logger(__name__)

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

VENUE_PROMPT = """
You are a venue research assistant. Given this event, return a JSON with:
- venue_name: full official name of the venue
- venue_address: full street address including city, country
- city: city name
- country: country name

Event: {name}
Location hint: {city}, {country}
Current venue info: {venue_name} — {venue_address}
"""


async def venue_agent(state: AgentState) -> AgentState:
    event = state.get("event")

    if not event:
        logger.info("venue_agent: no event in state, skipping")
        return {**state, "step": "venue_agent_skipped"}

    # Already has full venue info
    if event.get("venue_name") and event.get("venue_address"):
        logger.info(f"venue_agent: venue already complete for '{event['name']}'")
        return {**state, "step": "venue_agent_done"}

    logger.info(f"venue_agent: resolving venue for '{event['name']}'")

    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a venue research assistant. Return only valid JSON."},
                {"role": "user", "content": VENUE_PROMPT.format(
                    name=event.get("name", ""),
                    city=event.get("city", ""),
                    country=event.get("country", ""),
                    venue_name=event.get("venue_name", ""),
                    venue_address=event.get("venue_address", ""),
                )},
            ],
            response_format={"type": "json_object"},
            max_tokens=300,
            temperature=0,
        )
        data = json.loads(response.choices[0].message.content or "{}")

        updated_event: EventData = {
            **event,
            "venue_name": data.get("venue_name") or event.get("venue_name", ""),
            "venue_address": data.get("venue_address") or event.get("venue_address", ""),
            "city": data.get("city") or event.get("city", ""),
            "country": data.get("country") or event.get("country", ""),
        }

        logger.info(f"venue_agent: resolved venue '{updated_event['venue_name']}' at '{updated_event['venue_address']}'")
        return {**state, "event": updated_event, "step": "venue_agent_done"}

    except Exception as e:
        logger.error(f"venue_agent: failed: {e}")
        return {**state, "error": str(e), "step": "venue_agent_error"}


if __name__ == "__main__":
    state: AgentState = {
        "raw_event_input": None, "excel_path": None, "email_content": None,
        "event": {
            "id": "evt-001", "name": "Arab Health 2025", "type": "medical",
            "country": "UAE", "city": "Dubai", "venue_name": "",
            "venue_address": "", "start_date": "2025-01-27", "end_date": "2025-01-30",
            "source": "email",
        },
        "hotels": [], "vendor_prices": {}, "competitor_prices": {},
        "approval": None, "scores": None, "report": None, "error": None, "step": "start",
    }
    result = asyncio.run(venue_agent(state))
    print(result.get("event"))
