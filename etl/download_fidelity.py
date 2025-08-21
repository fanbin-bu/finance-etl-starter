
import os, asyncio
from dotenv import load_dotenv
from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from download_common import new_context, save_download, gen_totp

load_dotenv()

DOWNLOAD_DIR = "etl/downloads/fidelity"

async def run():
    user = os.getenv("FID_USER")
    pw = os.getenv("FID_PASS")
    totp_secret = os.getenv("FID_TOTP_SECRET")

    if not user or not pw:
        raise RuntimeError("Missing FID_USER or FID_PASS in environment/.env")

    ctx, pwlib = await new_context("fidelity", headless=True)
    page = await ctx.new_page()
    try:
        await page.goto("https://www.fidelity.com/", timeout=60000)
        # Click login
        try:
            await page.get_by_role("link", name="Log In").click(timeout=10000)
        except PlaywrightTimeoutError:
            await page.locator("text=Log In").first.click()

        await page.fill("input[name='username']", user)
        await page.fill("input[name='password']", pw)
        # Try multiple button labels just in case
        for label in ["Log in", "Sign In", "Submit"]:
            try:
                await page.get_by_role("button", name=label).click(timeout=3000)
                break
            except PlaywrightTimeoutError:
                pass

        # Handle OTP if prompted
        try:
            await page.wait_for_selector("input[name='otp']", timeout=5000)
            token = gen_totp(totp_secret)
            if not token:
                raise RuntimeError("TOTP required but FID_TOTP_SECRET not set")
            await page.fill("input[name='otp']", token)
            for label in ["Submit", "Verify", "Continue"]:
                try:
                    await page.get_by_role("button", name=label).click(timeout=3000)
                    break
                except PlaywrightTimeoutError:
                    pass
        except PlaywrightTimeoutError:
            pass  # no OTP

        # Navigate to download page (placeholder URL)
        try:
            await page.goto("https://oltx.fidelity.com/ftgw/fbc/ofx/download", timeout=60000)
        except PlaywrightTimeoutError:
            pass

        # TODO: Select date range & start QFX download. Replace selectors below after inspecting the page.
        # from playwright.async_api import expect
        # with page.expect_download() as dl_info:
        #     await page.get_by_role("button", name="Download Quicken/QFX").click()
        # download = await dl_info.value
        # await save_download(download, DOWNLOAD_DIR)

        print("[info] Update selectors in download_fidelity.py to trigger the QFX download on your account.")
    finally:
        await ctx.close()
        await pwlib.stop()

if __name__ == "__main__":
    asyncio.run(run())
