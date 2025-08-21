
import os, asyncio
from dotenv import load_dotenv
from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from download_common import new_context, save_download

load_dotenv()

DOWNLOAD_DIR = "etl/downloads/banks"

async def run():
    user = os.getenv("CITI_USER")
    pw = os.getenv("CITI_PASS")
    if not user or not pw:
        raise RuntimeError("Missing CITI_USER or CITI_PASS in environment/.env")

    ctx, pwlib = await new_context("citi", headless=True)
    page = await ctx.new_page()
    try:
        await page.goto("https://www.citi.com/", timeout=60000)
        # TODO: Complete login & export flow
        # await page.get_by_text("Sign On").click()
        # await page.fill("input[name='username']", user)
        # await page.fill("input[name='password']", pw)
        # await page.get_by_role("button", name="Sign On").click()

        # with page.expect_download() as dl_info:
        #     await page.get_by_text("Download").click()
        # download = await dl_info.value
        # await save_download(download, DOWNLOAD_DIR)

        print("[info] Update selectors in download_citi.py to login and export CSV.")
    finally:
        await ctx.close()
        await pwlib.stop()

if __name__ == "__main__":
    asyncio.run(run())
