"""Playwright scraper for Expedia hotel search."""
import asyncio
import random
from datetime import date

from playwright.async_api import async_playwright, TimeoutError as PWTimeout

from backend.utils.logger import get_logger

logger = get_logger(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
]


async def scrape_expedia(
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
            f"https://www.expedia.com/Hotel-Search"
            f"?destination={location.replace(' ', '+')}"
            f"&startDate={check_in.strftime('%Y-%m-%d')}"
            f"&endDate={check_out.strftime('%Y-%m-%d')}"
            f"&adults=1&rooms=1"
        )

        try:
            await page.goto(url, timeout=30000, wait_until="domcontentloaded")
            await asyncio.sleep(random.uniform(1.5, 3.0))

            try:
                await page.click('[data-stid="accept-button"]', timeout=3000)
            except PWTimeout:
                pass

            await page.wait_for_selector('[data-stid="property-listing"]', timeout=15000)
            cards = await page.query_selector_all('[data-stid="property-listing"]')

            for card in cards[:max_results]:
                try:
                    name_el = await card.query_selector('h3')
                    price_el = await card.query_selector('[data-stid="price-summary-message-trigger"]')
                    link_el = await card.query_selector('a')

                    name = (await name_el.inner_text()).strip() if name_el else "Unknown"
                    price_text = (await price_el.inner_text()).strip() if price_el else ""
                    href = await link_el.get_attribute("href") if link_el else ""

                    import re
                    nums = re.findall(r"[\d,]+(?:\.\d{1,2})?", price_text.replace(",", ""))
                    price = float(nums[0]) if nums else 0.0

                    results.append({
                        "name": name,
                        "market_price": price,
                        "rating": 0.0,
                        "booking_url": f"https://www.expedia.com{href}" if href.startswith("/") else href,
                        "source": "expedia.com",
                    })
                except Exception as e:
                    logger.warning(f"expedia_scraper: card parse error: {e}")

        except Exception as exc:
            logger.error(f"expedia_scraper: failed for {location}: {exc}")
        finally:
            await browser.close()

    logger.info(f"expedia_scraper: got {len(results)} hotels for '{location}'")
    return results
