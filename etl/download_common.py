
import os, asyncio, pathlib
from typing import Optional, Tuple
from dotenv import load_dotenv
import pyotp
from playwright.async_api import async_playwright, BrowserContext

load_dotenv()  # auto-load .env if present

def ensure_dir(path: str):
    pathlib.Path(path).mkdir(parents=True, exist_ok=True)

async def new_context(profile: str, headless: bool = True) -> Tuple[BrowserContext, any]:
    """Create a persistent Chromium context for a site profile. Returns (context, playwright)."""
    pw = await async_playwright().start()
    ctx = await pw.chromium.launch_persistent_context(
        user_data_dir=f"storage/state/{profile}",
        headless=headless,
        accept_downloads=True,
    )
    return ctx, pw

async def save_download(download, out_dir: str):
    ensure_dir(out_dir)
    suggested = await download.suggested_filename()
    out_path = os.path.join(out_dir, suggested or f"download_{int(asyncio.get_event_loop().time()*1e6)}")
    await download.save_as(out_path)
    print(f"[saved] {out_path}")
    return out_path

def gen_totp(secret: Optional[str]) -> Optional[str]:
    if not secret:
        return None
    return pyotp.TOTP(secret).now()
