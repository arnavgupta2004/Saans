// Records docs/assets/demo.gif from the deployed app at 375px:
// Today (replay) → swap card → Hindi notice → Ask with "✓ numbers checked".
// Usage (from frontend/): node scripts/demo_gif.mjs [baseUrl]   (needs ffmpeg on PATH)
import { chromium } from 'playwright';
import { execFileSync } from 'node:child_process';
import { mkdtemp, readdir, rm, stat } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const BASE = (process.argv[2] || 'https://main.d6f34l6r9rpi9.amplifyapp.com').replace(/\/+$/, '');
const API = 'https://qcx2qrt6bj.execute-api.us-east-1.amazonaws.com/api';
const OUT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../docs/assets/demo.gif');
const SIZE = { width: 375, height: 812 };
const QUESTION = 'Is PE at 8:40 safe?';

// Warm up Lambda + the model so the recorded answer arrives quickly.
await fetch(`${API}/schools/delhi-anand-vihar/today?replay=delhi-nov`);
await fetch(`${API}/ask`, { method: 'POST', headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ school_id: 'delhi-anand-vihar', question: QUESTION, lang: 'en', replay: 'delhi-nov' }) });

const dir = await mkdtemp(path.join(tmpdir(), 'saans-gif-'));
const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: SIZE, deviceScaleFactor: 1, recordVideo: { dir, size: SIZE } });
const page = await ctx.newPage();
const pause = (ms) => page.waitForTimeout(ms);
const smoothScroll = async (dy, steps = 12) => { for (let i = 0; i < steps; i++) { await page.mouse.wheel(0, dy / steps); await pause(40); } };

const t0 = Date.now();
await page.goto(`${BASE}/?replay=delhi-nov`, { waitUntil: 'networkidle' });
await page.locator('[data-testid="period-card"]').first().waitFor();
const startOffset = (Date.now() - t0) / 1000 + 0.9; // skip the blank load + skeleton (video starts slightly before t0)
await pause(2200);                                   // hero: 351 Very Poor · 2 changes needed
await page.mouse.move(187, 400);
await smoothScroll(560);                             // to the PE card + suggested swap
await pause(2600);

await page.locator('[data-tab="notice"]').click();
await page.getByRole('button', { name: 'हिंदी', exact: true }).click();
await page.getByText('प्रिय अभिभावकगण').waitFor({ timeout: 20000 });
await pause(2600);                                   // Hindi parent notice

await page.getByRole('button', { name: 'EN', exact: true }).click();
await page.locator('[data-tab="ask"]').click();
await pause(600);
await page.getByRole('textbox').click();
await page.keyboard.type(QUESTION, { delay: 45 });
await page.keyboard.press('Enter');
await page.locator('[data-testid="ask-answer"]').waitFor({ timeout: 35000 });
await pause(800);
await page.locator('[data-testid="ask-answer"]').scrollIntoViewIfNeeded();
await pause(3000);                                   // answer + ✓ numbers checked

const video = page.video();
await ctx.close();
await browser.close();
const webm = await video.path();

const palette = path.join(dir, 'palette.png');
const filters = 'fps=12,scale=375:-1:flags=lanczos';
execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-ss', String(startOffset), '-i', webm, '-vf', `${filters},palettegen=stats_mode=diff`, palette]);
execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-ss', String(startOffset), '-i', webm, '-i', palette,
  '-lavfi', `${filters} [x]; [x][1:v] paletteuse=dither=bayer:bayer_scale=5:diff_mode=rectangle`, '-loop', '0', OUT]);
const { size } = await stat(OUT);
console.log(`wrote ${OUT} (${(size / 1024 / 1024).toFixed(2)} MB)`);
console.log('frames dir cleaned:', (await readdir(dir)).length, 'files');
await rm(dir, { recursive: true, force: true });
