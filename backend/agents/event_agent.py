"""
Enriches or discovers event details from the web using GPT-4o + Playwright.
If event is already populated with dates and city, it just validates/enriches venue info.
"""
import asyncio
import json
import uuid
from typing import Optional

from openai import AsyncOpenAI

from backend.core.state import AgentState, EventData
from backend.config import settings
from backend.utils.logger import get_logger

logger = get_logger(__name__)

client = AsyncOpenAI(api_key=settings.OPENROUTER_API_KEY, base_url=settings.OPENROUTER_BASE_URL)

ENRICH_PROMPT = """
You are an event research assistant. Given this event information, fill in any missing fields.
Return JSON with these keys: name, type, country, city, venue_name, venue_address, start_date (YYYY-MM-DD), end_date (YYYY-MM-DD).
Only return what you know with confidence. Leave unknown fields as empty strings.

Known info:
{event_json}

Raw input:
{raw_input}
"""


async def _web_search_event(query: str) -> str:
    """Try to fetch event page content via Playwright for enrichment."""
    try:
        from playwright.async_api import async_playwright
        search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"

        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=settings.SCRAPER_HEADLESS)
            page = await browser.new_page()
            await page.goto(search_url, timeout=15000, wait_until="domcontentloaded")
            text = await page.inner_text("body")
            await browser.close()
            return text[:3000]
    except Exception as e:
        logger.warning(f"event_agent: web search failed: {e}")
        return ""


async def event_agent(state: AgentState) -> AgentState:
    event = state.get("event")
    raw = state.get("raw_event_input", "")

    # Nothing to work with
    if not event and not raw:
        logger.warning("event_agent: no event or raw_event_input, skipping")
        return {**state, "step": "event_agent_skipped"}

    # Event fully populated — just pass through
    if event and event.get("start_date") and event.get("city") and event.get("venue_name"):
        logger.info(f"event_agent: event fully populated, skipping enrichment for '{event['name']}'")
        return {**state, "step": "event_agent_done"}

    logger.info("event_agent: enriching event details via GPT-4o")

    search_text = ""
    if event:
        query = f"{event.get('name', '')} {event.get('city', '')} {event.get('country', '')} expo 2025"
        search_text = await _web_search_event(query)
    elif raw:
        search_text = raw

    try:
        response = await client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[
                {"role": "system", "content": "You are an event research assistant. Return only valid JSON."},
                {"role": "user", "content": ENRICH_PROMPT.format(
                    event_json=json.dumps(event or {}),
                    raw_input=search_text[:3000],
                )},
            ],
            response_format={"type": "json_object"},
            max_tokens=500,
            temperature=0,
        )
        data = json.loads(response.choices[0].message.content or "{}")

        base = event or {}
        enriched = EventData(
            id=base.get("id") or str(uuid.uuid4()),
            name=data.get("name") or base.get("name", "Unknown Event"),
            type=data.get("type") or base.get("type", "business"),
            country=data.get("country") or base.get("country", ""),
            city=data.get("city") or base.get("city", ""),
            venue_name=data.get("venue_name") or base.get("venue_name", ""),
            venue_address=data.get("venue_address") or base.get("venue_address", ""),
            start_date=data.get("start_date") or base.get("start_date", ""),
            end_date=data.get("end_date") or base.get("end_date", ""),
            source=base.get("source", "web_scrape"),
        )
        logger.info(f"event_agent: enriched event '{enriched['name']}'")
        return {**state, "event": enriched, "step": "event_agent_done"}

    except Exception as e:
        logger.error(f"event_agent: enrichment failed: {e}")
        return {**state, "error": str(e), "step": "event_agent_error"}


if __name__ == "__main__":
    state: AgentState = {
        "raw_event_input": "Arab Health 2025 Dubai January 27-30 Dubai World Trade Centre",
        "excel_path": None, "email_content": None, "event": None,
        "hotels": [], "vendor_prices": {}, "competitor_prices": {},
        "approval": None, "scores": None, "report": None, "error": None, "step": "start",
    }
    result = asyncio.run(event_agent(state))
    print(result.get("event"))
