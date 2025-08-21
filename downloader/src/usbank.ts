import { newPersistentContext, saveDownload } from './common.js';
import 'dotenv/config';

(async () => {
  const ctx = await newPersistentContext('usbank');
  const page = await ctx.newPage();
  await page.goto('https://onlinebanking.usbank.com/');

  // TODO: login using process.env.USB_USER / USB_PASS
  // TODO: navigate to transactions, set date range, trigger CSV export
  // const [download] = await Promise.all([
  //   page.waitForEvent('download'),
  //   page.click('text=Export')
  // ]);
  // await saveDownload(download, 'etl/downloads/banks');
  await ctx.close();
})();
