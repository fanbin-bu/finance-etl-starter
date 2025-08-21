import asyncio, os, pyotp
from playwright.async_api import async_playwright

async def login_with_otp(page, user, pw, otp_selector="input[name='otp']", totp_secret=None):
    await page.fill("input[name='username']", user)
    await page.fill("input[name='password']", pw)
    await page.click("button[type='submit']")
    if totp_secret:
        try:
            if await page.is_visible(otp_selector, timeout=3000):
                token = pyotp.TOTP(totp_secret).now()
                await page.fill(otp_selector, token)
                await page.click("button[type='submit']")
        except Exception:
            pass

async def run_site(profile, start_url, login_fn, download_fn):
    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=f"storage/state/{profile}",
            headless=True,
            accept_downloads=True
        )
        page = await browser.new_page()
        await page.goto(start_url)
        await login_fn(page)
        await download_fn(page)
        await browser.close()
