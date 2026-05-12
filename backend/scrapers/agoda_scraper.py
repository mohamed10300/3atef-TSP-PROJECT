"""Playwright scraper for Agoda hotel search."""
import asyncio
import random
from datetime import date

from playwright.async_api import async_playwright, TimeoutError as PWTimeout

from backend.utils.logger import get_logger

logger = get_logger(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
]


async def scrape_agoda(
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

        nights = 1
        url = (
            f"https://www.agoda.com/search"
            f"?city={location.replace(' ', '+')}"
            f"&checkIn={check_in.strftime('%Y-%m-%d')}"
            f"&los={nights}&rooms=1&adults=1&lang=en-us"
        )

        try:
            await page.goto(url, timeout=30000, wait_until="domcontentloaded")
            await asyncio.sleep(random.uniform(2.0, 4.0))

            await page.wait_for_selector('[data-selenium="hotel-item"]', timeout=15000)
            cards = await page.query_selector_all('[data-selenium="hotel-item"]')

            for card in cards[:max_results]:
                try:
                    name_el = await card.query_selector('[data-selenium="hotel-name"]')
                    price_el = await card.query_selector('[class*="price"]')
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
                        "booking_url": f"https://www.agoda.com{href}" if href.startswith("/") else href,
                        "source": "agoda.com",
                    })
                except Exception as e:
                    logger.warning(f"agoda_scraper: card parse error: {e}")

        except Exception as exc:
            logger.error(f"agoda_scraper: failed for {location}: {exc}")
        finally:
            await browser.close()

    logger.info(f"agoda_scraper: got {len(results)} hotels for '{location}'")
    return results
