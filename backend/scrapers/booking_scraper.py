"""
Playwright-based scraper for Booking.com hotel search.
Returns a list of hotel dicts near a given location for specific dates.
"""
import asyncio
import random
from datetime import date
from typing import Optional

from playwright.async_api import async_playwright, Browser, Page, TimeoutError as PWTimeout

from backend.utils.logger import get_logger

logger = get_logger(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
]


async def _random_delay(min_ms: int = 800, max_ms: int = 2500) -> None:
    await asyncio.sleep(random.uniform(min_ms / 1000, max_ms / 1000))


async def scrape_booking(
    location: str,
    check_in: date,
    check_out: date,
    max_results: int = 10,
    headless: bool = True,
) -> list[dict]:
    results: list[dict] = []

    async with async_playwright() as pw:
        browser: Browser = await pw.chromium.launch(headless=headless)
        ctx = await browser.new_context(
            user_agent=random.choice(USER_AGENTS),
            viewport={"width": 1280, "height": 900},
            locale="en-US",
        )
        page: Page = await ctx.new_page()

        check_in_str = check_in.strftime("%Y-%m-%d")
        check_out_str = check_out.strftime("%Y-%m-%d")
        url = (
            f"https://www.booking.com/searchresults.html"
            f"?ss={location.replace(' ', '+')}"
            f"&checkin={check_in_str}&checkout={check_out_str}"
            f"&group_adults=1&no_rooms=1&lang=en-us"
        )

        try:
            await page.goto(url, timeout=30000, wait_until="domcontentloaded")
            await _random_delay()

            # Dismiss cookie banner if present
            try:
                await page.click('[data-testid="accept-button"]', timeout=3000)
                await _random_delay(300, 800)
            except PWTimeout:
                pass

            await page.wait_for_selector('[data-testid="property-card"]', timeout=15000)

            cards = await page.query_selector_all('[data-testid="property-card"]')
            for card in cards[:max_results]:
                try:
                    name_el = await card.query_selector('[data-testid="title"]')
                    price_el = await card.query_selector('[data-testid="price-and-discounted-price"]')
                    score_el = await card.query_selector('[data-testid="review-score"]')
                    link_el = await card.query_selector('a[data-testid="title-link"]')

                    name = (await name_el.inner_text()).strip() if name_el else "Unknown"
                    price_text = (await price_el.inner_text()).strip() if price_el else ""
                    score_text = (await score_el.inner_text()).strip() if score_el else "0"
                    href = await link_el.get_attribute("href") if link_el else ""

                    price = _parse_price(price_text)
                    score = _parse_score(score_text)

                    results.append({
                        "name": name,
                        "market_price": price,
                        "rating": score,
                        "booking_url": href or url,
                        "source": "booking.com",
                    })
                except Exception as e:
                    logger.warning(f"booking_scraper: error parsing card: {e}")

        except Exception as exc:
            logger.error(f"booking_scraper: failed scraping {location}: {exc}")
        finally:
            await browser.close()

    logger.info(f"booking_scraper: got {len(results)} hotels for '{location}'")
    return results


def _parse_price(text: str) -> float:
    import re
    nums = re.findall(r"[\d,]+(?:\.\d{1,2})?", text.replace(",", ""))
    return float(nums[0]) if nums else 0.0


def _parse_score(text: str) -> float:
    import re
    nums = re.findall(r"\d+(?:\.\d)?", text)
    val = float(nums[0]) if nums else 0.0
    return round(val / 10 if val > 10 else val, 1)


if __name__ == "__main__":
    from datetime import date

    async def main():
        hotels = await scrape_booking("Dubai", date(2025, 3, 10), date(2025, 3, 14), max_results=5)
        for h in hotels:
            print(h)

    asyncio.run(main())
