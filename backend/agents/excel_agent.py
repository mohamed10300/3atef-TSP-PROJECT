"""
Reads an uploaded Excel file and populates vendor_prices and competitor_prices in state.
Expected sheets: "Vendor" (hotel_name, vendor_price, room_type) and "Competitor" (hotel_name, competitor_price).
"""
import asyncio
from typing import Optional

from backend.core.state import AgentState
from backend.utils.excel_parser import parse_vendor_sheet, parse_competitor_sheet
from backend.utils.logger import get_logger

logger = get_logger(__name__)


async def excel_agent(state: AgentState) -> AgentState:
    excel_path: Optional[str] = state.get("excel_path")

    if not excel_path:
        logger.info("excel_agent: no excel_path provided, skipping")
        return {**state, "step": "excel_agent_skipped"}

    try:
        vendor_prices = parse_vendor_sheet(excel_path)
        competitor_prices = parse_competitor_sheet(excel_path)

        logger.info(
            f"excel_agent: loaded {len(vendor_prices)} vendor rows, "
            f"{len(competitor_prices)} competitor rows from {excel_path}"
        )

        return {
            **state,
            "vendor_prices": vendor_prices,
            "competitor_prices": competitor_prices,
            "step": "excel_agent_done",
        }
    except Exception as exc:
        logger.error(f"excel_agent error: {exc}")
        return {**state, "error": str(exc), "step": "excel_agent_error"}


if __name__ == "__main__":
    import sys

    path = sys.argv[1] if len(sys.argv) > 1 else "sample_vendor.xlsx"

    state: AgentState = {
        "raw_event_input": None,
        "excel_path": path,
        "email_content": None,
        "event": None,
        "hotels": [],
        "vendor_prices": {},
        "competitor_prices": {},
        "approval": None,
        "scores": None,
        "report": None,
        "error": None,
        "step": "start",
    }

    result = asyncio.run(excel_agent(state))
    print("vendor_prices:", result.get("vendor_prices"))
    print("competitor_prices:", result.get("competitor_prices"))
    print("step:", result.get("step"))
