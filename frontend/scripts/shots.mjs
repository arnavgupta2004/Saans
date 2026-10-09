// Screenshot the deployed Saans app at phone size (375×812) into docs/img/.
// Usage (from frontend/): node scripts/shots.mjs [baseUrl]
//   default baseUrl: https://main.d6f34l6r9rpi9.amplifyapp.com
import { chromium } from 'playwright';
import { mkdir } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const BASE = (process.argv[2] || process.env.SHOTS_URL || 'https://main.d6f34l6r9rpi9.amplifyapp.com').replace(/\/+$/, '');
const OUT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../docs/img');
const VIEWPORT = { width: 375, height: 812 };

const tab = (page, name) => page.locator(`nav [data-tab="${name}"], button:has-text("${name[0].toUpperCase() + name.slice(1)}")`).first();

async function waitForPlan(page) {
  // Today is ready when a period card or an error/retry state is visible.
  await page.locator('[data-testid="period-card"], h3, button:has-text("Retry")').first().waitFor({ timeout: 30000 });
  await page.waitForTimeout(600);
}

async function shot(page, name) {
  const file = path.join(OUT, `${name}.png`);
  await page.screenshot({ path: file, fullPage: true });
  // Also flag horizontal overflow, which breaks the phone layout.
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
  console.log(`${name}.png${overflow > 0 ? `  ⚠ horizontal overflow ${overflow}px` : ''}`);
}

async function enableReplay(page) {
  await page.goto(`${BASE}/?replay=delhi-nov`, { waitUntil: 'networkidle' });
  await waitForPlan(page);
  if (!(await page.getByText(/Replay: recorded data/).count())) {
    await page.getByRole('button', { name: /Try a bad-air day/i }).click();
    await page.getByText(/Replay: recorded data/).waitFor({ timeout: 30000 });
    await page.waitForTimeout(600);
  }
}

const browser = await chromium.launch();
await mkdir(OUT, { recursive: true });
const ctx = await browser.newContext({ viewport: VIEWPORT, deviceScaleFactor: 2, locale: 'en-IN', timezoneId: 'Asia/Kolkata' });
const page = await ctx.newPage();
page.on('pageerror', (e) => console.log('  page error:', e.message));

// Today (live)
await page.goto(BASE, { waitUntil: 'networkidle' });
await waitForPlan(page);
await shot(page, 'today-live');

// Today (replay)
await enableReplay(page);
await shot(page, 'today-replay');

// Week
await page.goto(BASE, { waitUntil: 'networkidle' });
await waitForPlan(page);
await tab(page, 'week').click();
await page.waitForTimeout(4000);
await shot(page, 'week');

// Notice EN + HI
await tab(page, 'notice').click();
await page.waitForTimeout(4000);
await shot(page, 'notice-en');
await page.getByRole('button', { name: /हिंदी/ }).first().click();
await page.waitForTimeout(4000);
await shot(page, 'notice-hi');
await page.getByRole('button', { name: /^\s*EN\s*$/ }).first().click().catch(() => {});

// Ask (replay context)
await enableReplay(page);
await tab(page, 'ask').click();
await page.getByRole('textbox').fill('Is PE at 8:40 safe?');
await page.keyboard.press('Enter');
await page.waitForTimeout(1500);
await shot(page, 'ask-waiting');
await page.waitForSelector('[data-testid="ask-answer"], .whitespace-pre-line', { timeout: 35000 });
await page.waitForTimeout(500);
await shot(page, 'ask-answer');

// Setup
await tab(page, 'setup').click();
await page.waitForTimeout(1500);
await shot(page, 'setup');

await browser.close();
console.log(`saved to ${OUT}`);
