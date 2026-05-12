"""
Reads email content from state (or fetches from Outlook/Gmail via Microsoft Graph / Gmail API)
and extracts structured event data using GPT-4o.
"""
import asyncio
import json
import uuid
from typing import Optional

from openai import AsyncOpenAI

from backend.core.state import AgentState, EventData
from backend.config import settings
from backend.utils.email_parser import detect_country, detect_event_type, extract_expo_name
from backend.utils.logger import get_logger

logger = get_logger(__name__)

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

EXTRACTION_PROMPT = """
Extract event information from this email content. Return JSON with these exact keys:
- name: event name
- type: one of [medical, pharma, health, tech, industrial, business]
- country: country where event takes place
- city: city where event takes place
- venue_name: name of the venue/hall/center
- venue_address: full address if available, else empty string
- start_date: ISO date string YYYY-MM-DD or empty string
- end_date: ISO date string YYYY-MM-DD or empty string

Email content:
{content}
"""


async def _extract_event_from_email(email_text: str) -> Optional[EventData]:
    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an event data extraction assistant. Return only valid JSON."},
                {"role": "user", "content": EXTRACTION_PROMPT.format(content=email_text[:6000])},
            ],
            response_format={"type": "json_object"},
            max_tokens=600,
            temperature=0,
        )
        data = json.loads(response.choices[0].message.content or "{}")
        return EventData(
            id=str(uuid.uuid4()),
            name=data.get("name") or extract_expo_name(email_text),
            type=data.get("type") or detect_event_type(email_text),
            country=data.get("country") or detect_country(email_text),
            city=data.get("city", ""),
            venue_name=data.get("venue_name", ""),
            venue_address=data.get("venue_address", ""),
            start_date=data.get("start_date", ""),
            end_date=data.get("end_date", ""),
            source="email",
        )
    except Exception as e:
        logger.error(f"email_agent: GPT extraction failed: {e}")
        return None


async def email_agent(state: AgentState) -> AgentState:
    email_content: Optional[str] = state.get("email_content")

    # If event already populated (e.g. from manual input), skip
    if state.get("event"):
        logger.info("email_agent: event already set, skipping")
        return {**state, "step": "email_agent_skipped"}

    if not email_content:
        logger.info("email_agent: no email_content in state, skipping")
        return {**state, "step": "email_agent_skipped"}

    logger.info("email_agent: extracting event from email content")
    event = await _extract_event_from_email(email_content)

    if not event:
        return {**state, "error": "email_agent: could not extract event", "step": "email_agent_error"}

    logger.info(f"email_agent: extracted event '{event['name']}' in {event['city']}, {event['country']}")
    return {**state, "event": event, "step": "email_agent_done"}


if __name__ == "__main__":
    sample_email = """
    Subject: Invitation — Arab Health 2025

    Dear Partner,

    We are pleased to invite you to Arab Health 2025, the world's largest gathering of healthcare and medical professionals.

    Event: Arab Health 2025
    Venue: Dubai World Trade Centre, Dubai, UAE
    Dates: 27 – 30 January 2025

    Please confirm your attendance.
    """

    state: AgentState = {
        "raw_event_input": None, "excel_path": None,
        "email_content": sample_email, "event": None,
        "hotels": [], "vendor_prices": {}, "competitor_prices": {},
        "approval": None, "scores": None, "report": None, "error": None, "step": "start",
    }

    result = asyncio.run(email_agent(state))
    print(result.get("event"))
