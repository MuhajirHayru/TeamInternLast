import os
import django
import asyncio
from playwright.async_api import async_playwright

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "TeamInternLast.settings")
django.setup()

from Teamworkapp.models import TikTokProfile

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://www.tiktok.com/@muhajirhayru", timeout=60000)

        followers = await page.inner_text('strong[data-e2e="followers-count"]')
        following = await page.inner_text('strong[data-e2e="following-count"]')
        likes = await page.inner_text('strong[data-e2e="likes-count"]')

        # Save to database
        profile, created = TikTokProfile.objects.update_or_create(
            username="muhajirhayru",
            defaults={
                "followers": int(followers.replace(",", "")),
                "following": int(following.replace(",", "")),
                "likes": int(likes.replace(",", "")),
                "videos": 0,  # add scraping for videos if needed
            }
        )
        print("Saved:", profile)

        await browser.close()

asyncio.run(run())