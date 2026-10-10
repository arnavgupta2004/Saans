# Saans — 3:00 demo video

> **Superseded (10 Oct):** the video is now generated: `node docs/video/make_video.mjs` → `video/saans-demo.mp4` (clean) + `video/saans-demo-prompter.mp4` (read-along). The voice-over to read is **`docs/video/SCRIPT.md`** (generated from `docs/video/scenes.mjs`). The table below is the original plan.

Pace: ~100–110 words per minute with pauses, short sentences. Total voice-over ≈ 285 words, leaving room to breathe.
Record the app in a **phone-sized browser window (375×812)**, screen at 1080p. Captions are burned in (many judges watch muted).

## Shot list and voice-over

| Time | Shot (what is on screen) | Voice-over | On-screen caption |
|---|---|---|---|
| **0:00–0:15** | Title card: Saans wordmark, tagline "Air-smart school day". Fade to a photo/clip of a hazy school ground (own or free-licensed). | "It is a winter morning in Delhi. The air is at its worst. And at 8:40, Class 7B goes out for PE." | Saans — AQI-smart timetables for schools |
| **0:15–0:35** | Problem card with two lines + sources (WHO 2018; Lancet Planetary Health 2024; GRAP IV school closure, Nov 2024). | "Children breathe more air for their size than adults. Schools today get two options. A normal day, or school closed. Nothing tells the principal what to do with period two." | 93% of children live above WHO air guidelines (WHO, 2018) |
| **0:35–0:50** | App: `?replay=delhi-nov`. Purple banner "Replay: recorded Delhi air, 19 Nov 2025". Hero: **351 Very Poor**, "2 changes needed today". | "This is Saans. Here is a real bad day, recorded in Delhi on 19 November 2025. Air quality now: 351. Very Poor. Two changes needed today." | Recorded data · 19 Nov 2025 · Anand Vihar, Delhi |
| **0:50–1:20** | Scroll slowly: Assembly card (house icon, "Hold assembly indoors; use the PA system or classrooms"), Class 7B PE card, blue **Suggested swap: Class 7B PE 08:40 ⇄ Period 8 13:40 · AQI 351 → 127**. Pause on the swap. Then the asthma line. | "Saans reads the hourly forecast for the school. It applies India's AQI, and a clear school protocol. Assembly moves indoors. And for PE, Saans finds a cleaner hour. Swap with Period 8 at 1:40. The AQI drops from 351 to 127. Students with asthma get their own, stricter advice." | Same day, different hour: AQI 351 → 127 |
| **1:20–1:30** | Scroll to bottom: "6 indoor classes — no change needed", source line "recorded Open-Meteo data… not calibrated". | "Indoor classes stay as they are. And every screen says where the numbers come from." | Every number shows its source |
| **1:30–1:50** | Notice tab (EN) → tap **हिंदी** in the header → Hindi notice → hover/tap **Share on WhatsApp**. | "One tap gives parents a notice. In English, or in Hindi. It offers the swap. It does not pretend it is decided. Then share on WhatsApp." | Parent notice · EN / हिंदी · WhatsApp |
| **1:50–2:20** | Ask tab (still replay). Type or tap "Is PE at 8:40 safe?". Show progress steps ("Reading today's plan…"). Answer appears: AQI 351, "Hold PE indoors", "Suggested move… Period 8 13:40… 127". Zoom on **✓ numbers checked against the replayed plan** and the model name. | "Ask Saans is an AI agent built with Strands Agents. It answers from the same plan, using tools. And then we check its work. Every number in the answer must match the plan. If it does not, Saans shows the plan itself." | AI explains · rules decide · numbers checked |
| **2:20–2:35** | Back to live (`Back to live`). Today live: big AQI, amber note "Not calibrated: … nearest CPCB monitor via OpenAQ last reported 53 h ago". Quick cut to Week view tiles. | "On a live day, Saans calibrates against government monitors when the reading is fresh. When it is not, it tells you so. Honestly." | Calibrated only with fresh reference monitors |
| **2:35–2:52** | Architecture diagram (README mermaid, rendered) with AWS icons. | "It runs on AWS. Lambda and API Gateway for the API. DynamoDB for schools and daily plans. EventBridge Scheduler runs it at 6 AM, India time. CloudWatch and SNS alert us. Amplify hosts the app. All deployed with AWS SAM." | Lambda · API Gateway · DynamoDB · EventBridge · CloudWatch + SNS · Amplify · SAM · Strands |
| **2:52–3:00** | End card: Saans wordmark, live URL, "Team Chernobyl". | "Saans. Cleaner hours for every child. Team Chernobyl." | main.d6f34l6r9rpi9.amplifyapp.com · Team Chernobyl |

## Direct links for each shot

- Replay Today: `https://main.d6f34l6r9rpi9.amplifyapp.com/?replay=delhi-nov`
- Replay Ask: `https://main.d6f34l6r9rpi9.amplifyapp.com/?replay=delhi-nov&tab=ask`
- Replay Notice in Hindi: `https://main.d6f34l6r9rpi9.amplifyapp.com/?replay=delhi-nov&tab=notice&lang=hi`
- Live Today: `https://main.d6f34l6r9rpi9.amplifyapp.com/`
- Week: `https://main.d6f34l6r9rpi9.amplifyapp.com/?tab=week`

## Pre-recording checklist

- [ ] **Warm up the API** 2 minutes before: open the live URL once and the replay URL once (avoids a Lambda cold start on camera).
- [ ] **Warm up Ask:** ask "Is PE at 8:40 safe?" on the replay day once. Confirm the answer shows **✓ numbers checked** and a model name. If it shows the plan summary instead, wait a minute and retry (Gemini load).
- [ ] **Phone-sized window:** Chrome DevTools → device toolbar → 375×812, zoom 100%. Hide the DevTools panel itself (undock) or use a separate window sized to 375×812.
- [ ] **Language = EN** at the start (header toggle), school = **Anand Vihar**.
- [ ] Open the replay link fresh, so the purple banner is visible at the top.
- [ ] Clear browser notifications, close other tabs, hide bookmarks bar.
- [ ] Have the architecture diagram rendered (GitHub README view or exported PNG) in a second tab.
- [ ] Check the live Today screen first: if live air is very clean, keep the live segment short — the replay day carries the story.
- [ ] Record voice-over separately, in a quiet room; read from this script; then cut video to the voice.
- [ ] Captions: burn in the "On-screen caption" column; keep each up for the whole shot.
- [ ] Final check: total 3:00 or less, URL readable on the end card, no API keys or terminal windows visible anywhere.
