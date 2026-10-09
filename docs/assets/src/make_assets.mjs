// Renders docs/assets/{architecture,title-card,end-card}.png at 1920×1080.
// Usage (from repo root):
//   PUPPETEER_SKIP_DOWNLOAD=1 npx -y @mermaid-js/mermaid-cli@11.4.2 -i docs/assets/src/architecture.mmd \
//     -o docs/assets/src/architecture.svg -p docs/assets/src/puppeteer.json -c docs/assets/src/mermaid.json -b transparent
//   node docs/assets/src/make_assets.mjs
import { chromium } from '../../../frontend/node_modules/playwright/index.mjs';
import { readFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const OUT = path.resolve(HERE, '..');
const LIVE = 'main.d6f34l6r9rpi9.amplifyapp.com';

const WIND = `<svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12.8 19.6A2 2 0 1 0 14 16H2"/><path d="M17.5 8a2.5 2.5 0 1 1 2 4H2"/><path d="M9.8 4.4A2 2 0 1 1 11 8H2"/></svg>`;

const BASE_CSS = `
  * { box-sizing: border-box; margin: 0; }
  body { width: 1920px; height: 1080px; background: #FAFAF9; font-family: Inter, -apple-system, 'Helvetica Neue', Arial, sans-serif; color: #1C1917; }
  .logo { display: inline-grid; place-items: center; border-radius: 9999px; background: #0D9488; }
  .logo svg { width: 58%; height: 58%; }
`;

const card = ({ kicker, title, sub, lines, foot }) => `<!doctype html><html><head><meta charset="utf-8"><style>${BASE_CSS}
  .wrap { height: 100%; display: flex; flex-direction: column; justify-content: center; padding: 0 180px; position: relative; }
  .brand { display: flex; align-items: center; gap: 28px; }
  .brand .logo { width: 120px; height: 120px; }
  .brand span { font-size: 112px; font-weight: 600; letter-spacing: -3px; }
  .kicker { margin-top: 56px; font-size: 30px; font-weight: 600; letter-spacing: 4px; text-transform: uppercase; color: #0F766E; }
  h1 { margin-top: 18px; font-size: 76px; font-weight: 600; letter-spacing: -1.5px; line-height: 1.1; max-width: 1500px; }
  .sub { margin-top: 26px; font-size: 36px; color: #57534E; max-width: 1400px; line-height: 1.35; }
  .lines { margin-top: 64px; display: flex; gap: 20px; flex-wrap: wrap; }
  .pill { font-size: 30px; padding: 14px 26px; border-radius: 9999px; background: white; border: 2px solid #E7E5E4; color: #44403C; }
  .pill b { color: #0F766E; font-weight: 600; }
  .foot { position: absolute; left: 180px; right: 180px; bottom: 80px; display: flex; justify-content: space-between; font-size: 26px; color: #78716C; }
  .bar { position: absolute; left: 0; right: 0; top: 0; height: 14px; background: linear-gradient(90deg, #50CCAA, #CEE59B, #FFD666, #FF9933, #FF3333, #CC0000); }
</style></head><body><div class="bar"></div><div class="wrap">
  <div class="brand"><span class="logo">${WIND}</span><span>Saans</span></div>
  <div class="kicker">${kicker}</div>
  <h1>${title}</h1>
  <div class="sub">${sub}</div>
  <div class="lines">${lines.map((l) => `<div class="pill">${l}</div>`).join('')}</div>
  <div class="foot">${foot}</div>
</div></body></html>`;

const architecture = (svg) => `<!doctype html><html><head><meta charset="utf-8"><style>${BASE_CSS}
  .head { position: absolute; left: 90px; top: 64px; display: flex; align-items: center; gap: 22px; }
  .head .logo { width: 64px; height: 64px; }
  .head h1 { font-size: 52px; font-weight: 600; letter-spacing: -1px; }
  .head p { font-size: 26px; color: #78716C; margin-left: 12px; }
  .diagram { position: absolute; left: 70px; right: 70px; top: 170px; bottom: 110px; display: grid; place-items: center; }
  .diagram svg { width: 100% !important; height: 100% !important; max-width: none !important; }
  .legend { position: absolute; left: 90px; bottom: 48px; display: flex; gap: 40px; font-size: 24px; color: #57534E; }
  .sw { display: inline-block; width: 26px; height: 26px; border-radius: 6px; vertical-align: -5px; margin-right: 10px; border: 2px solid; }
</style></head><body>
  <div class="head"><span class="logo">${WIND}</span><h1>Saans on AWS</h1><p>one SAM template · serverless · 06:00 IST daily run</p></div>
  <div class="diagram">${svg}</div>
  <div class="legend">
    <span><i class="sw" style="background:#FFF7ED;border-color:#EA580C"></i>AWS service</span>
    <span><i class="sw" style="background:#F0FDFA;border-color:#0F766E"></i>Saans logic (rules decide, AI explains)</span>
    <span><i class="sw" style="background:#F5F5F4;border-color:#A8A29E"></i>External data / model</span>
  </div>
</body></html>`;

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });

async function render(html, file) {
  await page.setContent(html, { waitUntil: 'load' });
  await page.screenshot({ path: path.join(OUT, file) });
  console.log('wrote', file);
}

await render(card({
  kicker: 'Air · Environmental Hacks',
  title: 'AQI-smart timetables for schools',
  sub: 'Hour-by-hour air forecasts turned into decisions for each period — which class moves indoors, which moves to a cleaner hour, and what to tell parents.',
  lines: ['<b>Track 01</b> · Air — school safety on bad days', '<b>Team</b> Chernobyl', 'WeMakeDevs × AWS'],
  foot: `<span>Built on AWS · Strands Agents</span><span>${LIVE}</span>`,
}), 'title-card.png');

await render(card({
  kicker: 'Cleaner hours for every child',
  title: 'AQI-smart timetables for schools',
  sub: `Try it: <b style="color:#0F766E">${LIVE}</b><br/>Bad-air day replay: ${LIVE}/?replay=delhi-nov`,
  lines: ['Air · Environmental Hacks', '<b>Team</b> Chernobyl', 'Lambda · API Gateway · DynamoDB · EventBridge · Amplify · SAM'],
  foot: '<span>Rules decide. AI explains. Numbers checked.</span><span>Thank you</span>',
}), 'end-card.png');

const svg = (await readFile(path.join(HERE, 'architecture.svg'), 'utf8')).replace(/<\?xml[^>]*>/, '');
await render(architecture(svg), 'architecture.png');

await browser.close();
