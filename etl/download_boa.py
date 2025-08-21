import asyncio
import os

from dotenv import load_dotenv
from download_common import new_context, save_download

load_dotenv()

DOWNLOAD_DIR = "etl/downloads/banks"


async def run():
    user = os.getenv("BOA_USER")
    pw = os.getenv("BOA_PASS")
    if not user or not pw:
        raise RuntimeError("Missing BOA_USER or BOA_PASS in environment/.env")

    ctx, pwlib = await new_context("boa", headless=True)
    page = await ctx.new_page()
    try:
        await page.goto("https://www.bankofamerica.com/", timeout=60000)
        print("[debug] Navigated to Bank of America homepage")

        # TODO: Complete login & export flow with your selectors
        # await page.get_by_role("button", name="Sign In").click()
        print("[debug] Filling login credentials")
        await page.fill("input[name='onlineId1']", user)
        await page.fill("input[name='passcode1']", pw)
        await page.get_by_role("button", name="Log In").click()
        print("[debug] Clicked login button")

        # Wait for login to complete and check current URL/title
        try:
            await page.wait_for_load_state("networkidle", timeout=15000)
        except Exception as e:
            print(f"[warning] Page load timeout: {e}")
            print("[debug] Continuing anyway...")

        await asyncio.sleep(3)  # Give it a bit more time
        current_url = page.url
        page_title = await page.title()
        print(f"[debug] Login completed - Current URL: {current_url}")
        print(f"[debug] Page title: {page_title}")

        # Handle 2FA if needed
        if "Authorization Code Request" in page_title:
            print("[debug] 2FA required - requesting SMS code")

            # First, let's see what's actually on the page
            page_content = await page.content()
            print(f"[debug] 2FA page content length: {len(page_content)}")

            # Look for all clickable elements
            all_buttons = await page.locator(
                "button, input[type='button'], input[type='submit']"
            ).all()
            print(f"[debug] Found {len(all_buttons)} buttons on 2FA page")
            for i, btn in enumerate(all_buttons[:10]):  # Show first 10
                try:
                    text = await btn.text_content() or ""
                    value = await btn.get_attribute("value") or ""
                    btn_type = await btn.get_attribute("type") or ""
                    print(
                        f"[debug] Button {i}: text='{text}' value='{value}' type='{btn_type}'"
                    )
                except:
                    print(f"[debug] Button {i}: Could not get info")

            # Try to select SMS option and send to phone number 6122066582
            try:
                # Look for SMS/text option
                await page.locator("input[id='rbText']").click()
                print("[debug] Selected SMS option")

                # Look for the phone number option (6122066582)
                await page.get_by_text("6582").click()  # Last 4 digits should be visible
                print("[debug] Selected phone number ending in 6582")

                # Click send code button
                await page.get_by_text("Send Code").click()
                print("[debug] Requested SMS code")

                # Wait for code input field
                await page.wait_for_selector("input[type='text']", timeout=10000)
                print("[info] SMS code sent! Please check your phone.")

                # Prompt user for code
                auth_code = input("Enter the 6-digit authorization code from SMS: ")

                # Enter the code
                await page.fill("input[type='text']", auth_code)
                print(f"[debug] Entered code: {auth_code}")

                # Try multiple submit button selectors
                submit_selectors = [
                    "button:has-text('Submit')",
                    "input[value='Submit']",
                    "button[type='submit']",
                    "input[type='submit']",
                    "*:has-text('Submit')",
                ]

                submitted = False
                for selector in submit_selectors:
                    try:
                        submit_button = page.locator(selector)
                        if await submit_button.count() > 0:
                            await submit_button.first.click()
                            print(f"[debug] Clicked submit using selector: {selector}")
                            submitted = True
                            break
                    except Exception as e:
                        print(f"[debug] Submit selector {selector} failed: {e}")

                if not submitted:
                    print("[warning] Could not find submit button - trying Enter key")
                    await page.keyboard.press("Enter")

                print("[debug] Submitted authorization code")

                # Wait for page to load after 2FA
                await page.wait_for_load_state("networkidle")
                print(f"[debug] After 2FA - URL: {page.url}")
                print(f"[debug] After 2FA - Title: {await page.title()}")

            except Exception as e:
                print(f"[warning] 2FA handling failed: {e}")
                print("[info] You may need to manually complete 2FA or update selectors")

        # Handle session timeout dialog if present
        try:
            # Look for "OK" button in timeout dialog - try multiple approaches
            ok_selectors = [
                "button:has-text('OK')",
                "button:has-text('Ok')",
                "button:has-text('ok')",
                "input[value='OK']",
                "input[value='Ok']",
                "input[value='ok']",
                "[role='button']:has-text('OK')",
                "*:has-text('OK')",
            ]
            for selector in ok_selectors:
                ok_button = page.locator(selector)
                if await ok_button.count() > 0:
                    await ok_button.first.click()
                    print(f"[debug] Clicked OK button using selector: {selector}")
                    await asyncio.sleep(2)
                    break
        except Exception as e:
            print(f"[debug] No session dialog found: {e}")

        # Handle security preference dialog if present
        try:
            # Look for security preference options - try multiple approaches
            yes_selectors = [
                "button:has-text('Yes')",
                "button:has-text('YES')",
                "button:has-text('yes')",
                "input[value='Yes']",
                "input[value='YES']",
                "input[value='yes']",
                "[role='button']:has-text('Yes')",
                "*:has-text('Yes')",
            ]
            for selector in yes_selectors:
                yes_button = page.locator(selector)
                if await yes_button.count() > 0:
                    await yes_button.first.click()
                    print(f"[debug] Selected Yes option using selector: {selector}")
                    await asyncio.sleep(2)
                    break
        except Exception as e:
            print(f"[debug] No security preference dialog found: {e}")

        # Additional wait and refresh check
        await asyncio.sleep(3)
        print("[debug] Checking if we're now on the main banking page...")

        # Debug: Show page content to see what's available
        current_url = page.url
        page_title = await page.title()
        print(f"[debug] Current URL after dialogs: {current_url}")
        print(f"[debug] Current title after dialogs: {page_title}")

        # Check if we're still on 2FA page - continue with 2FA process
        if "Authorization Code Request" in page_title:
            print(
                "[debug] Still on 2FA page after dialog handling - continuing with 2FA process"
            )

            # First, let's see what's actually on the page
            page_content = await page.content()
            print(f"[debug] 2FA page content length: {len(page_content)}")

            # Look for all clickable elements
            all_buttons = await page.locator(
                "button, input[type='button'], input[type='submit']"
            ).all()
            print(f"[debug] Found {len(all_buttons)} buttons on 2FA page")
            for i, btn in enumerate(all_buttons[:10]):  # Show first 10
                try:
                    text = await btn.text_content() or ""
                    value = await btn.get_attribute("value") or ""
                    btn_type = await btn.get_attribute("type") or ""
                    print(
                        f"[debug] Button {i}: text='{text}' value='{value}' type='{btn_type}'"
                    )
                except Exception:
                    print(f"[debug] Button {i}: Could not get info")

            # Try to select SMS option and send to phone number 6122066582
            try:
                # Look for SMS/text option
                await page.locator("input[id='rbText']").click()
                print("[debug] Selected SMS option")

                # Look for the phone number option (6122066582)
                await page.get_by_text("6582").click()  # Last 4 digits should be visible
                print("[debug] Selected phone number ending in 6582")

                # Click send code button
                await page.get_by_text("Send Code").click()
                print("[debug] Requested SMS code")

                # Wait for code input field
                await page.wait_for_selector("input[type='text']", timeout=10000)
                print("[info] SMS code sent! Please check your phone.")

                # Prompt user for code
                auth_code = input("Enter the 6-digit authorization code from SMS: ")

                # Enter the code
                await page.fill("input[type='text']", auth_code)
                print(f"[debug] Entered code: {auth_code}")

                # Try multiple submit button selectors
                submit_selectors = [
                    "button:has-text('Submit')",
                    "input[value='Submit']",
                    "button[type='submit']",
                    "input[type='submit']",
                    "*:has-text('Submit')",
                ]

                submitted = False
                for selector in submit_selectors:
                    try:
                        submit_button = page.locator(selector)
                        if await submit_button.count() > 0:
                            await submit_button.first.click()
                            print(f"[debug] Clicked submit using selector: {selector}")
                            submitted = True
                            break
                    except Exception as e:
                        print(f"[debug] Submit selector {selector} failed: {e}")

                if not submitted:
                    print("[warning] Could not find submit button - trying Enter key")
                    await page.keyboard.press("Enter")

                print("[debug] Submitted authorization code")

                # Wait for page to load after 2FA
                await page.wait_for_load_state("networkidle")
                print(f"[debug] After 2FA - URL: {page.url}")
                print(f"[debug] After 2FA - Title: {await page.title()}")

            except Exception as e:
                print(f"[warning] 2FA handling failed: {e}")
                print("[info] You may need to manually complete 2FA or update selectors")
                return

        # Try to find account elements
        accounts = await page.locator("text=/.*banking.*/i").all()
        print(f"[debug] Found {len(accounts)} potential account elements")
        for i, account in enumerate(accounts[:5]):  # Show first 5
            text = await account.text_content()
            print(f"[debug] Account {i}: {text}")

        async with page.expect_download() as dl_info:
            # Click on the specific account
            await page.get_by_text("Adv Plus Banking - 8998").click()
            await page.get_by_text("Download").click()
            await page.get_by_text("Select a timeframe").click()
            await page.get_by_text("Current transactions").click()
            await page.get_by_text("Select file type").click()
            await page.get_by_text("Download").click()
        download = await dl_info.value
        await save_download(download, DOWNLOAD_DIR)

        print("[info] Update selectors in download_boa.py to login and export CSV.")
    finally:
        await ctx.close()
        await pwlib.stop()


if __name__ == "__main__":
    asyncio.run(run())
