import { chromium, BrowserContext } from 'playwright';
import 'dotenv/config';
import * as path from 'path';
import * as fs from 'fs';
import { authenticator } from 'otplib';

async function ensureDir(p: string) {
  await fs.promises.mkdir(p, { recursive: true });
}

// Reusable browser context with persistent storage to minimize 2FA prompts
export async function newPersistentContext(profile: string) : Promise<BrowserContext> {
  const userDataDir = path.resolve(`downloader_state/${profile}`);
  await ensureDir(userDataDir);
  const ctx = await chromium.launchPersistentContext(userDataDir, {
    headless: true,
    acceptDownloads: true,
  });
  return ctx;
}

export async function saveDownload(download, outDir: string) {
  await ensureDir(outDir);
  const suggested = await download.suggestedFilename();
  const outPath = path.join(outDir, suggested || `download_${Date.now()}`);
  await download.saveAs(outPath);
  console.log(`[saved] ${outPath}`);
}

export function genTotp(secret?: string) {
  if (!secret) return null;
  return authenticator.generate(secret);
}
