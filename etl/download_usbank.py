
import os, asyncio
from dotenv import load_dotenv
from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from download_common import new_context, save_download

load_dotenv()

DOWNLOAD_DIR = "etl/downloads/banks"

async def run():
    user = os.getenv("USB_USER")
    pw = os.getenv("USB_PASS")
    if not user or not pw:
        raise RuntimeError("Missing USB_USER or USB_PASS in environment/.env")

    ctx, pwlib = await new_context("usbank", headless=True)
    page = await ctx.new_page()
    try:
        await page.goto("https://onlinebanking.usbank.com/", timeout=60000)
        # TODO: Complete login & export flow
        # await page.fill("input[name='username']", user)
        # await page.fill("input[name='password']", pw)
        # await page.get_by_role("button", name="Log in").click()

        # with page.expect_download() as dl_info:
        #     await page.get_by_text("Export").click()
        # download = await dl_info.value
        # await save_download(download, DOWNLOAD_DIR)

        print("[info] Update selectors in download_usbank.py to login and export CSV.")
    finally:
        await ctx.close()
        await pwlib.stop()

if __name__ == "__main__":
    asyncio.run(run())
