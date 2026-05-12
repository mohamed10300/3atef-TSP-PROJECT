"""Utilities for parsing raw email content into structured event hints."""
import re
from typing import Optional


DATE_PATTERN = re.compile(
    r"\b(\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{4}[-/]\d{2}[-/]\d{2}|"
    r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\.?\s+\d{1,2},?\s+\d{4})\b",
    re.IGNORECASE,
)

COUNTRY_HINTS = [
    "UAE", "United Arab Emirates", "Saudi Arabia", "Germany", "France", "USA",
    "United States", "UK", "United Kingdom", "Japan", "China", "India", "Egypt",
    "Italy", "Spain", "Netherlands", "Switzerland", "Singapore", "Australia",
]

EVENT_TYPE_KEYWORDS = {
    "medical": ["medical", "medicine", "healthcare", "clinical", "hospital"],
    "pharma": ["pharma", "pharmaceutical", "drug", "biotech", "biopharma"],
    "health": ["health", "wellness", "nutrition", "fitness"],
    "tech": ["tech", "technology", "it ", "software", "digital", "ai ", "robotics"],
    "industrial": ["industrial", "manufacturing", "engineering", "factory", "machinery"],
    "business": ["business", "trade", "commerce", "finance", "investment"],
}


def extract_dates(text: str) -> list[str]:
    return DATE_PATTERN.findall(text)


def detect_country(text: str) -> str:
    for country in COUNTRY_HINTS:
        if country.lower() in text.lower():
            return country
    return ""


def detect_event_type(text: str) -> str:
    lower = text.lower()
    for event_type, keywords in EVENT_TYPE_KEYWORDS.items():
        if any(kw in lower for kw in keywords):
            return event_type
    return "business"


def extract_expo_name(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    for line in lines[:10]:
        if any(kw in line.lower() for kw in ["expo", "conference", "summit", "congress", "fair", "show"]):
            return line[:200]
    return lines[0][:200] if lines else "Unknown Event"
