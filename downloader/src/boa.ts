import { newPersistentContext, saveDownload } from './common.js';
import 'dotenv/config';

// Skeleton — you must inspect BOA DOM once to finalize selectors & download URL.
(async () => {
  const ctx = await newPersistentContext('boa');
  const page = await ctx.newPage();
  await page.goto('https://www.bankofamerica.com/');

  // TODO: navigate to login, submit credentials from env
  // await page.fill('input[name="onlineId"]', process.env.BOA_USER!);
  // await page.fill('input[name="passcode"]', process.env.BOA_PASS!);
  // await page.click('button[type="submit"]');

  // TODO: navigate to activity page and click Export/Download CSV for desired date range
  // const [download] = await Promise.all([
  //   page.waitForEvent('download'),
  //   page.click('text=Download CSV')
  // ]);
  // await saveDownload(download, 'etl/downloads/banks');

  await ctx.close();
})();
