"""Playwright scraper for Google Hotels search."""
import asyncio
import random
from datetime import date

from playwright.async_api import async_playwright, TimeoutError as PWTimeout

from backend.utils.logger import get_logger

logger = get_logger(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
]


async def scrape_google_hotels(
    location: str,
    check_in: date,
    check_out: date,
    max_results: int = 10,
    headless: bool = True,
) -> list[dict]:
    results: list[dict] = []

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=headless)
        ctx = await browser.new_context(
            user_agent=random.choice(USER_AGENTS),
            viewport={"width": 1280, "height": 900},
            locale="en-US",
        )
        page = await ctx.new_page()

        url = (
            f"https://www.google.com/travel/hotels"
            f"?q=hotels+in+{location.replace(' ', '+')}"
            f"&checkin={check_in.strftime('%Y-%m-%d')}"
            f"&checkout={check_out.strftime('%Y-%m-%d')}"
        )

        try:
            await page.goto(url, timeout=30000, wait_until="domcontentloaded")
            await asyncio.sleep(random.uniform(2.0, 3.5))

            cards = await page.query_selector_all('[data-hveid]')
            for card in cards[:max_results]:
                try:
                    name_el = await card.query_selector('h2, h3')
                    price_el = await card.query_selector('[data-price]')

                    name = (await name_el.inner_text()).strip() if name_el else "Unknown"
                    price_text = (await price_el.inner_text()).strip() if price_el else ""

                    import re
                    nums = re.findall(r"[\d,]+(?:\.\d{1,2})?", price_text.replace(",", ""))
                    price = float(nums[0]) if nums else 0.0

                    if name and price:
                        results.append({
                            "name": name,
                            "market_price": price,
                            "rating": 0.0,
                            "booking_url": url,
                            "source": "google_hotels",
                        })
                except Exception as e:
                    logger.warning(f"google_hotels: card parse error: {e}")

        except Exception as exc:
            logger.error(f"google_hotels: failed for {location}: {exc}")
        finally:
            await browser.close()

    logger.info(f"google_hotels: got {len(results)} hotels for '{location}'")
    return results
