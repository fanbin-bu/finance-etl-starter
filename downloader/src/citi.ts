import { newPersistentContext, saveDownload } from './common.js';
import 'dotenv/config';

(async () => {
  const ctx = await newPersistentContext('citi');
  const page = await ctx.newPage();
  await page.goto('https://www.citi.com/');

  // TODO: login using process.env.CITI_USER / CITI_PASS
  // TODO: navigate to statements or activity export (CSV/QFX)
  // const [download] = await Promise.all([
  //   page.waitForEvent('download'),
  //   page.click('text=Download')
  // ]);
  // await saveDownload(download, 'etl/downloads/banks');

  await ctx.close();
})();
