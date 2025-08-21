import { newPersistentContext, saveDownload, genTotp } from './common.js';
import 'dotenv/config';

(async () => {
  const ctx = await newPersistentContext('fidelity');
  const page = await ctx.newPage();
  await page.goto('https://www.fidelity.com/');

  // Click login and authenticate
  // await page.click('text=Log In');
  // await page.fill('input[name="username"]', process.env.FID_USER!);
  // await page.fill('input[name="password"]', process.env.FID_PASS!);
  // await page.click('button[type="submit"]');

  // Optional TOTP:
  // const token = genTotp(process.env.FID_TOTP_SECRET);
  // if (token && await page.isVisible('input[name="otp"]').catch(() => false)) {
  //   await page.fill('input[name="otp"]', token);
  //   await page.click('button[type="submit"]');
  // }

  // Go to activity / downloads area and request QFX/OFX for a date range
  // await page.goto('https://oltx.fidelity.com/ftgw/fbc/ofx/download'); // placeholder
  // const [download] = await Promise.all([
  //   page.waitForEvent('download'),
  //   page.click('text=Download Quicken/QFX') // replace with exact selector
  // ]);
  // await saveDownload(download, 'etl/downloads/fidelity');

  await ctx.close();
})();
