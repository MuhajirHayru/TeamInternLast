# scraper.py
from playwright.async_api import async_playwright

async def scrape_tiktok_profile(username: str) -> dict:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(f"https://www.tiktok.com/@{username}", timeout=60000)

        followers = await page.inner_text('strong[data-e2e="followers-count"]')
        following = await page.inner_text('strong[data-e2e="following-count"]')
        likes = await page.inner_text('strong[data-e2e="likes-count"]')
        videos = len(await page.query_selector_all('div[data-e2e="user-post-item"]'))

        await browser.close()

        return {
            "followers": int(followers.replace(",", "")),
            "following": int(following.replace(",", "")),
            "likes": int(likes.replace(",", "")),
            "videos": videos,
        }