"""
Uses GPT-4o to extract refund/cancellation/no-show policy text from each hotel's booking page.
Falls back to placeholder text if scraping the policy page fails.
"""
import asyncio
from openai import AsyncOpenAI

from backend.core.state import AgentState, HotelData
from backend.config import settings
from backend.utils.logger import get_logger

logger = get_logger(__name__)

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

POLICY_PROMPT = """
You are analyzing a hotel booking page. Extract the following policy information as plain text:
1. Refund policy
2. Cancellation penalty
3. No-show policy

Return JSON with keys: refund_policy, cancellation_penalty, no_show_policy.
If information is not available, use "Not specified".

Page content:
{content}
"""


async def _fetch_policy_text(url: str) -> str:
    """Attempt to fetch policy text from a booking URL using Playwright."""
    if not url:
        return ""
    try:
        from playwright.async_api import async_playwright
        import random

        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=settings.SCRAPER_HEADLESS)
            ctx = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            )
            page = await ctx.new_page()
            await page.goto(url, timeout=20000, wait_until="domcontentloaded")
            await asyncio.sleep(random.uniform(1.0, 2.0))
            text = await page.inner_text("body")
            await browser.close()
            # Keep only the relevant chunk
            return text[:4000]
    except Exception as e:
        logger.warning(f"policy_agent: could not fetch policy from {url}: {e}")
        return ""


async def _extract_policy(hotel: HotelData) -> HotelData:
    content = await _fetch_policy_text(hotel.get("booking_url", ""))
    if not content:
        return hotel

    try:
        import json
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a hotel policy extraction assistant. Return only valid JSON."},
                {"role": "user", "content": POLICY_PROMPT.format(content=content)},
            ],
            response_format={"type": "json_object"},
            max_tokens=400,
            temperature=0,
        )
        data = json.loads(response.choices[0].message.content or "{}")
        return {
            **hotel,
            "refund_policy": data.get("refund_policy", hotel.get("refund_policy", "")),
            "cancellation_penalty": data.get("cancellation_penalty", hotel.get("cancellation_penalty", "")),
            "no_show_policy": data.get("no_show_policy", hotel.get("no_show_policy", "")),
        }
    except Exception as e:
        logger.warning(f"policy_agent: GPT extraction failed for {hotel['name']}: {e}")
        return hotel


async def policy_agent(state: AgentState) -> AgentState:
    hotels = state.get("hotels", [])

    if not hotels:
        return {**state, "step": "policy_agent_skipped"}

    logger.info(f"policy_agent: extracting policies for {len(hotels)} hotels")

    updated = await asyncio.gather(*[_extract_policy(h) for h in hotels])

    return {**state, "hotels": list(updated), "step": "policy_agent_done"}


if __name__ == "__main__":
    import asyncio
    from backend.core.state import HotelData

    sample: HotelData = {
        "id": "1", "event_id": "e1", "name": "Test Hotel", "address": "",
        "distance_from_venue_km": 0.5, "rating": 4.0, "room_type": "Standard",
        "market_price": 90.0, "vendor_price": 100.0, "competitor_price": 95.0,
        "price_difference": -10.0, "is_cheaper_than_vendor": True,
        "refund_policy": "", "cancellation_penalty": "", "no_show_policy": "",
        "availability": True, "booking_url": "",
    }

    state: AgentState = {
        "raw_event_input": None, "excel_path": None, "email_content": None,
        "event": None, "hotels": [sample],
        "vendor_prices": {}, "competitor_prices": {},
        "approval": None, "scores": None, "report": None, "error": None, "step": "start",
    }

    result = asyncio.run(policy_agent(state))
    print(result["hotels"][0])
