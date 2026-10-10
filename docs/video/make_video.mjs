// Builds the 1920×1080 demo video from the live app (replay day + live day), timed to docs/video/scenes.mjs.
// Outputs (git-ignored):  video/saans-demo.mp4           — clean video to submit (silent; add your voice-over)
//                         video/saans-demo-prompter.mp4  — same timeline with the line to read at the bottom
// Usage (repo root, needs ffmpeg):  node docs/video/make_video.mjs [workDir]
import { chromium } from '../../frontend/node_modules/playwright/index.mjs';
import { execFileSync } from 'node:child_process';
import { mkdirSync, rmSync, writeFileSync, statSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { SCENES, XFADE, starts, mmss } from './scenes.mjs';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const WORK = path.resolve(process.argv[2] || path.join(tmpdir(), 'saans-video'));
const OUT = path.join(ROOT, 'video');
const BASE = 'https://main.d6f34l6r9rpi9.amplifyapp.com';
const API = 'https://qcx2qrt6bj.execute-api.us-east-1.amazonaws.com/api';
const QUESTION = 'Is PE at 8:40 safe?';
const SCREEN = { x: 1236, y: 90, w: 416, h: 900 };   // phone screen on the 1920×1080 canvas (375×812 @ 1.11)
const BG = '#FAFAF9';
rmSync(WORK, { recursive: true, force: true });
mkdirSync(path.join(WORK, 'frames'), { recursive: true });
mkdirSync(OUT, { recursive: true });
const ff = (args) => execFileSync('ffmpeg', ['-y', '-loglevel', 'error', ...args], { stdio: 'inherit' });
const esc = (s) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;');

// ---------- 1. Stills: caption layers (with a phone-shaped hole), problem slide, prompter strips ----------
const WIND = `<svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12.8 19.6A2 2 0 1 0 14 16H2"/><path d="M17.5 8a2.5 2.5 0 1 1 2 4H2"/><path d="M9.8 4.4A2 2 0 1 1 11 8H2"/></svg>`;
const CSS = `*{box-sizing:border-box;margin:0} body{width:1920px;height:1080px;background:transparent;font-family:Inter,-apple-system,'Helvetica Neue',Arial,sans-serif;color:#1C1917;overflow:hidden;position:relative}
 .logo{display:inline-grid;place-items:center;border-radius:9999px;background:#0D9488}.logo svg{width:58%;height:58%}
 .bar{position:absolute;left:0;right:0;top:0;height:10px;background:linear-gradient(90deg,#50CCAA,#CEE59B,#FFD666,#FF9933,#FF3333,#CC0000);z-index:3}`;

const appLayer = (s, i) => `<!doctype html><html><head><meta charset="utf-8"><style>${CSS}
 .hole{position:absolute;left:${SCREEN.x}px;top:${SCREEN.y}px;width:${SCREEN.w}px;height:${SCREEN.h}px;border-radius:44px;
   box-shadow:0 0 0 14px #1C1917,0 0 0 15px #44403C,0 30px 80px 20px rgba(28,25,23,.18),0 0 0 3000px ${BG}}
 .left{position:absolute;left:140px;top:0;bottom:0;width:960px;display:flex;flex-direction:column;justify-content:center;z-index:2}
 .brand{position:absolute;left:140px;top:72px;display:flex;align-items:center;gap:16px;z-index:2}.brand .logo{width:52px;height:52px}.brand span{font-size:40px;font-weight:600;letter-spacing:-1px}
 .k{font-size:28px;font-weight:600;letter-spacing:3px;text-transform:uppercase;color:#0F766E}
 h1{margin-top:22px;font-size:72px;line-height:1.08;font-weight:650;letter-spacing:-1.5px}
 .sub{margin-top:30px;font-size:34px;line-height:1.4;color:#57534E;max-width:900px}
 .foot{position:absolute;left:140px;bottom:64px;font-size:24px;color:#A8A29E;z-index:2}
 .dots{display:flex;gap:10px;margin-top:56px}.dots i{width:40px;height:6px;border-radius:3px;background:#E7E5E4}.dots i.on{background:#0D9488}
</style></head><body><div class="bar"></div><div class="hole"></div>
 <div class="brand"><span class="logo">${WIND}</span><span>Saans</span></div>
 <div class="left"><div class="k">${esc(s.kicker)}</div><h1>${esc(s.caption)}</h1><div class="sub">${esc(s.sub)}</div>
   <div class="dots">${SCENES.filter((x) => x.kind === 'app').map((x) => `<i class="${x.id === s.id ? 'on' : ''}"></i>`).join('')}</div></div>
 <div class="foot">Team Chernobyl · Track 01 Air · ${BASE.replace('https://', '')}</div>
</body></html>`;

const problem = `<!doctype html><html><head><meta charset="utf-8"><style>${CSS} body{background:${BG}}
 .wrap{position:absolute;inset:0;padding:120px 160px;display:flex;flex-direction:column;justify-content:center}
 .k{font-size:30px;font-weight:600;letter-spacing:4px;text-transform:uppercase;color:#B91C1C}
 h1{margin-top:20px;font-size:68px;line-height:1.1;font-weight:650;letter-spacing:-1.5px;max-width:1500px}
 .cards{margin-top:64px;display:grid;grid-template-columns:repeat(3,1fr);gap:32px}
 .c{background:white;border:2px solid #E7E5E4;border-radius:28px;padding:36px 36px 30px}
 .n{font-size:64px;font-weight:700;color:#B91C1C;letter-spacing:-1px}.t{margin-top:12px;font-size:28px;line-height:1.35;color:#292524}
 .s{margin-top:18px;font-size:20px;color:#A8A29E}
 .q{margin-top:60px;font-size:40px;font-weight:600;color:#0F766E}
</style></head><body><div class="bar"></div><div class="wrap">
 <div class="k">The problem</div>
 <h1>On bad-air days, schools get two options: a normal day, or school closed.</h1>
 <div class="cards">
  <div class="c"><div class="n">93%</div><div class="t">of the world’s children under 15 breathe air above WHO guideline levels</div><div class="s">WHO, Air pollution and child health, 2018</div></div>
  <div class="c"><div class="n">10 cities</div><div class="t">Short-term rises in PM2.5 linked to more daily deaths across ten Indian cities</div><div class="s">Lancet Planetary Health, 2024</div></div>
  <div class="c"><div class="n">AQI 441</div><div class="t">Delhi, 17 Nov 2024: GRAP Stage IV suspends physical classes across Delhi-NCR</div><div class="s">CAQM GRAP order, Nov 2024</div></div>
 </div>
 <div class="q">Nothing tells the principal what to do with the 8:40 PE period.</div>
</div></body></html>`;

const strip = (s, i, at) => {
  const next = SCENES[i + 1];
  return `<!doctype html><html><head><meta charset="utf-8"><style>${CSS} body{height:290px}
  .s{position:absolute;inset:0;background:rgba(12,10,9,.88);padding:22px 60px;color:white}
  .h{font-size:22px;color:#FBBF24;font-weight:600;letter-spacing:1px}.v{margin-top:8px;font-size:35px;line-height:1.3;font-weight:500}
  .n{position:absolute;left:60px;right:60px;bottom:18px;font-size:21px;color:#A8A29E;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
 </style></head><body><div class="s"><div class="h">READ NOW · ${mmss(at)}–${mmss(at + s.dur)} · scene ${i + 1}/${SCENES.length}</div>
  <div class="v">${esc(s.vo)}</div><div class="n">${next ? `NEXT (${mmss(at + s.dur)}): ${esc(next.vo)}` : 'END — stop recording'}</div></div></body></html>`;
};

const browser = await chromium.launch();
{
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  const shot = async (html, file, opts = {}) => { await page.setContent(html, { waitUntil: 'load' }); await page.screenshot({ path: path.join(WORK, file), omitBackground: true, ...opts }); };
  await shot(problem, 'problem.png');
  const at = starts();
  for (const [i, s] of SCENES.entries()) {
    if (s.kind === 'app') await shot(appLayer(s, i), `layer_${s.id}.png`);
    await shot(strip(s, i, at[i]), `strip_${i}.png`, { clip: { x: 0, y: 0, width: 1920, height: 290 } });
  }
  await page.close();
}

// ---------- 2. Record the app via CDP screencast (crisp 2× frames with timestamps) ----------
await fetch(`${API}/schools/delhi-anand-vihar/today?replay=delhi-nov`);
await fetch(`${API}/schools/delhi-anand-vihar/today`);
await fetch(`${API}/schools/delhi-anand-vihar/week`);
await fetch(`${API}/ask`, { method: 'POST', headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ school_id: 'delhi-anand-vihar', question: QUESTION, lang: 'en', replay: 'delhi-nov' }) });

async function record() {
  rmSync(path.join(WORK, 'frames'), { recursive: true, force: true }); mkdirSync(path.join(WORK, 'frames'));
  const ctx = await browser.newContext({ viewport: { width: 375, height: 812 }, deviceScaleFactor: 2 });
  const page = await ctx.newPage();
  const cdp = await ctx.newCDPSession(page);
  const frames = []; let n = 0;
  cdp.on('Page.screencastFrame', ({ data, metadata, sessionId }) => {
    const file = path.join(WORK, 'frames', `${String(n++).padStart(5, '0')}.jpg`);
    writeFileSync(file, Buffer.from(data, 'base64'));
    frames.push({ file, ts: metadata.timestamp });
    cdp.send('Page.screencastFrameAck', { sessionId }).catch(() => {});
  });
  await cdp.send('Page.startScreencast', { format: 'jpeg', quality: 92, maxWidth: 750, maxHeight: 1624 });

  const marks = {}; let t0 = 0;
  let cur = null;
  const begin = (id) => { t0 = Date.now() / 1000; cur = id; marks[id] = { start: t0, skips: [] }; };
  // Cut a slow wait (e.g. a 6 s API call) out of the video; scene timing continues as if it took no time.
  const skip = async (fn) => { const a = Date.now() / 1000; await fn(); const b = Date.now() / 1000; marks[cur].skips.push([a, b]); t0 += b - a; };
  const end = (id) => { marks[id].end = Date.now() / 1000; };
  const at = async (sec) => { const ms = (t0 + sec) * 1000 - Date.now(); if (ms > 0) await page.waitForTimeout(ms); };
  const scrollTo = (sel, off, ms) => page.evaluate(async ([sel, off, ms]) => {
    const el = sel ? document.querySelector(sel) : null;
    let sc = el && el.parentElement;
    while (sc && !(sc.scrollHeight > sc.clientHeight + 4 && /(auto|scroll)/.test(getComputedStyle(sc).overflowY))) sc = sc.parentElement;
    const doc = !sc; sc = sc || document.scrollingElement;
    const from = sc.scrollTop;
    const target = el ? from + el.getBoundingClientRect().top - (doc ? 0 : sc.getBoundingClientRect().top) - off : sc.scrollHeight;
    const to = Math.max(0, Math.min(target, sc.scrollHeight - sc.clientHeight));
    const s = performance.now();
    await new Promise((r) => { const step = (now) => { const p = Math.min(1, (now - s) / ms); const e = p < 0.5 ? 2 * p * p : 1 - (-2 * p + 2) ** 2 / 2; sc.scrollTop = from + (to - from) * e; p < 1 ? requestAnimationFrame(step) : r(); }; requestAnimationFrame(step); });
  }, [sel, off, ms]);
  const tag = (locator, name) => locator.first().evaluate((el, name) => el.setAttribute('data-v', name), name);

  // (unrecorded) load the replay day
  await page.goto(`${BASE}/?replay=delhi-nov&school=delhi-anand-vihar`, { waitUntil: 'networkidle' });
  await page.locator('[data-testid="period-card"]').first().waitFor();
  await page.waitForTimeout(1200);

  begin('hero'); await at(15); end('hero');

  begin('swap');
  await tag(page.locator('[data-testid="period-card"]').nth(0), 'assembly');
  await tag(page.locator('[data-testid="period-card"]').nth(1), 'pe');
  await at(1.5); await scrollTo('[data-v="assembly"]', 84, 1500);
  await at(9); await scrollTo('[data-v="pe"]', 84, 1800);
  await at(26); end('swap');

  begin('impact');
  await at(0.3); await scrollTo('[data-testid="impact-card"]', 96, 1300);
  await at(4); await page.locator('[data-testid="impact-card"] summary').click();
  await at(14); end('impact');

  begin('source');
  await at(0.3); await scrollTo(null, 0, 2000);
  await at(9); end('source');

  begin('notice');
  await at(0.3); await page.locator('[data-tab="notice"]').click();
  await at(6.5); await page.getByRole('button', { name: 'हिंदी', exact: true }).click();
  await page.getByText('प्रिय अभिभावकगण').waitFor({ timeout: 20000 });
  await at(13); await tag(page.locator('a[href*="wa.me"], a[href*="whatsapp"]'), 'wa');
  await scrollTo('[data-v="wa"]', 420, 1300); await page.locator('[data-v="wa"]').hover();
  await at(19); end('notice');

  await page.getByRole('button', { name: 'EN', exact: true }).click();            // (unrecorded) back to English
  await page.waitForTimeout(800);

  begin('ask');
  await at(0.3); await page.locator('[data-tab="ask"]').click();
  await at(1.8); await page.getByRole('textbox').click();
  await page.keyboard.type(QUESTION, { delay: 70 });
  await at(4.2); await page.keyboard.press('Enter');
  await page.locator('[data-testid="ask-answer"]').waitFor({ timeout: 40000 });
  await page.waitForTimeout(600);
  await page.locator('[data-testid="ask-answer"]').scrollIntoViewIfNeeded();
  const answer = await page.locator('[data-testid="ask-answer"]').innerText();
  await at(28); end('ask');

  // (unrecorded) back to live
  await page.goto(`${BASE}/?school=delhi-anand-vihar`, { waitUntil: 'networkidle' });
  await page.locator('[data-testid="period-card"]').first().waitFor();
  await page.waitForTimeout(1200);

  begin('live');
  await at(0.8); await scrollTo(null, 0, 1800);
  await at(8); await page.locator('[data-tab="week"]').click();
  await page.waitForTimeout(250);
  await skip(async () => { await page.locator('[data-testid="week-impact"]').waitFor({ timeout: 30000 }); await page.waitForTimeout(500); });
  await at(14); end('live');

  await cdp.send('Page.stopScreencast');
  await ctx.close();
  return { frames, marks, answer };
}

let rec;
for (let attempt = 1; attempt <= 3; attempt++) {
  rec = await record();
  if (/numbers checked/i.test(rec.answer)) break;
  console.log(`attempt ${attempt}: Ask answer not verified, retrying…`, rec.answer.slice(0, 80));
}
if (!/numbers checked/i.test(rec.answer)) throw new Error('Ask never returned a verified answer; not building a misleading video');
await browser.close();
console.log('ask answer:', rec.answer.replace(/\n+/g, ' | ').slice(0, 200));

// ---------- 3. Compose scenes, cross-fade, write outputs ----------
const segs = [];
for (const [i, s] of SCENES.entries()) {
  const len = s.dur + (i < SCENES.length - 1 ? XFADE : 0);
  const out = path.join(WORK, `seg_${i}.mp4`);
  const enc = ['-r', '30', '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', '-t', len.toFixed(3), out];
  if (s.kind === 'slide') {
    const img = s.image === 'problem' ? path.join(WORK, 'problem.png') : path.join(ROOT, s.image);
    ff(['-loop', '1', '-i', img, '-vf', 'scale=1920:1080:flags=lanczos,fps=30,format=yuv420p', ...enc]);
  } else {
    const { start, end, skips } = rec.marks[s.id];
    const fr = rec.frames;
    const prev = [...fr].reverse().find((f) => f.ts < start) || fr[0];
    const skipped = (ts) => skips.reduce((acc, [a, b]) => acc + (ts >= b ? b - a : 0), 0);
    const inSkip = (ts) => skips.some(([a, b]) => ts >= a && ts < b);
    const kept = fr.filter((f) => f.ts >= start && f.ts < end && !inSkip(f.ts));
    // the screen as it was when each cut ended (the frame that finished loading may fall inside the cut)
    for (const [, b] of skips) { const last = [...fr].reverse().find((f) => f.ts < b); if (last) kept.push({ file: last.file, ts: b }); }
    kept.sort((x, y) => x.ts - y.ts);
    const list = [{ file: prev.file, t: 0 }, ...kept.map((f) => ({ file: f.file, t: f.ts - start - skipped(f.ts) }))];
    const natural = end - start - skipped(end);
    const k = natural > len ? len / natural : 1;
    let txt = '';
    list.forEach((f, j) => {
      const d = j < list.length - 1 ? (list[j + 1].t - f.t) * k : Math.max(0.04, len - f.t * k);
      txt += `file '${f.file}'\nduration ${Math.max(0.001, d).toFixed(4)}\n`;
    });
    txt += `file '${list[list.length - 1].file}'\n`;
    writeFileSync(path.join(WORK, `list_${i}.txt`), txt);
    ff(['-f', 'lavfi', '-i', `color=c=${BG.slice(1)}:s=1920x1080:r=30`, '-f', 'concat', '-safe', '0', '-i', path.join(WORK, `list_${i}.txt`),
      '-loop', '1', '-i', path.join(WORK, `layer_${s.id}.png`),
      '-filter_complex', `[1:v]fps=30,scale=${SCREEN.w}:${SCREEN.h}:flags=lanczos,setpts=PTS-STARTPTS[s];[0:v][s]overlay=${SCREEN.x}:${SCREEN.y}:eof_action=repeat[a];[a][2:v]overlay=0:0,format=yuv420p[v]`,
      '-map', '[v]', ...enc]);
  }
  segs.push(out);
}

const at = starts();
let graph = ''; let last = '0:v';
for (let i = 1; i < segs.length; i++) {
  const lbl = i === segs.length - 1 ? 'v' : `x${i}`;
  graph += `[${last}][${i}:v]xfade=transition=fade:duration=${XFADE}:offset=${at[i].toFixed(3)}[${lbl}];`;
  last = lbl;
}
const total = at[at.length - 1] + SCENES[SCENES.length - 1].dur;
const clean = path.join(OUT, 'saans-demo.mp4');
ff([...segs.flatMap((s) => ['-i', s]), '-f', 'lavfi', '-t', String(total), '-i', 'anullsrc=r=48000:cl=stereo',
  '-filter_complex', graph.replace(/;$/, ''), '-map', '[v]', '-map', `${segs.length}:a`,
  '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '128k',
  '-t', String(total), '-movflags', '+faststart', clean]);

// Prompter copy: the line to read, plus a bar showing time left in the scene.
let pg = ''; let pl = '0:v';
SCENES.forEach((s, i) => {
  const a = at[i], b = a + s.dur, lbl = `p${i}`;
  pg += `[${pl}][${i + 1}:v]overlay=0:790:enable='between(t,${a},${b - 0.001})'[q${i}];`;
  pg += `[q${i}]drawbox=x=0:y=1074:w='max(1,1920*(t-${a})/${s.dur})':h=6:color=0xFBBF24@1:t=fill:enable='between(t,${a},${b - 0.001})'[${lbl}];`;
  pl = lbl;
});
ff(['-i', clean, ...SCENES.flatMap((_, i) => ['-loop', '1', '-t', String(total), '-i', path.join(WORK, `strip_${i}.png`)]),
  '-filter_complex', pg.replace(/;$/, ''), '-map', `[${pl}]`, '-map', '0:a', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '24',
  '-pix_fmt', 'yuv420p', '-c:a', 'copy', '-t', String(total), path.join(OUT, 'saans-demo-prompter.mp4')]);

for (const f of ['saans-demo.mp4', 'saans-demo-prompter.mp4']) console.log(`wrote video/${f} (${(statSync(path.join(OUT, f)).size / 1048576).toFixed(1)} MB, ${mmss(total)})`);
