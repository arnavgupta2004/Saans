# Submission form — copy-paste text

> Fill the placeholder `<BLOG_URL>` and make the GitHub repo public before submitting.

## Project name
Saans — AQI-smart timetables for schools

## Track
Track 01 · Air — "School safety on bad days"

## Team
Chernobyl — Arnav Gupta (lead), Avishi

## One-liner
Saans turns the hour-by-hour air-quality forecast into decisions for a school's actual timetable — which period moves indoors, which moves to a cleaner hour, and what to tell parents in English and Hindi.

## Description (150 words)
On bad-air days, schools in North India get two options: a normal day, or school closed. Saans fills the gap in between. It reads the hourly PM2.5/PM10 forecast for a school's location, converts it to India's National AQI, and runs every outdoor period through a deterministic, tested school protocol: go, take precautions, or move indoors. When PE falls in the worst hour, Saans suggests exchanging it with an indoor class at a cleaner hour — "Class 7B PE 08:40 ⇄ Period 8 13:40 · AQI 351 → 127". Students with asthma get stricter advice. Principals share a bilingual parent notice on WhatsApp in one tap. An AI assistant built with Strands Agents answers planning questions using the same planner as tools, and every number it states is checked against the plan. It runs serverless on AWS, with a 06:00 IST scheduled run, so the plan is ready before school starts.

## Problem
Air pollution peaks hour by hour, not day by day: in Delhi's winter, PM2.5 builds up overnight and falls after the morning mixing layer rises. Children are especially exposed — WHO reports that 93% of the world's children live with air pollution above its guideline levels, and a 2024 Lancet Planetary Health study across ten Indian cities linked short-term PM2.5 rises to higher daily mortality. Yet schools get blunt tools: when Delhi's AQI hit 441 on 17 Nov 2024, GRAP Stage IV closed physical classes across Delhi-NCR. On the many bad days that are not closure days, nothing tells a principal what to do with the 8:40 PE period.

## How it works
1. **Forecast:** hourly PM2.5/PM10 for the school's coordinates (Open-Meteo, CAMS model), converted to CPCB National AQI.
2. **Calibration:** corrected with the nearest CPCB reference monitor (data.gov.in, then OpenAQ) only when the reading is under 2 hours old and within 25 km; otherwise shown as uncalibrated, with the reason.
3. **Rules decide:** a deterministic protocol (activity intensity × AQI band, plus a stricter column for students with asthma) gives each outdoor period go / caution / indoors.
4. **Exchange swaps:** periods that must not run outdoors are exchanged with an indoor class at the cleanest available hour the same day.
5. **Communicate:** a bilingual EN/HI parent notice with a WhatsApp share link; a week view and best-day finder for events.
6. **AI explains:** a Strands agent answers questions by calling the planner as tools; a number guard replaces any answer containing numbers not found in the tool outputs with the deterministic plan summary.
7. **Daily run:** EventBridge Scheduler precomputes every school's plan at 06:00 IST.

## AWS services used
- **AWS Lambda** — the FastAPI API (via Mangum) and the 06:00 daily job.
- **Amazon API Gateway (HTTP API)** — public HTTPS endpoint with CORS.
- **Amazon DynamoDB** — school profiles and the cache of precomputed daily plans.
- **Amazon EventBridge Scheduler** — `cron(0 6 * * ? *)` in `Asia/Kolkata`.
- **Amazon CloudWatch + Amazon SNS** — Lambda error alarms with email alerts.
- **AWS Amplify Hosting** — the React frontend, rebuilt on every push.
- **AWS SAM** — the entire backend as one template, secrets as NoEcho parameters.
- **Strands Agents (AWS open source)** — the AI assistant and its tools. Amazon Bedrock (Nova Lite) is a supported provider; the live demo uses Gemini because Bedrock access was blocked on our account.

## What's next
- A small fetcher outside AWS that brings fresh CPCB readings into the cache, so calibration runs live again.
- Teachers enter their own timetables; "apply swap" writes back to the timetable.
- A 06:00 WhatsApp/SMS notice channel for parents.
- Validate the school thresholds with paediatricians and pilot with a few Delhi schools this winter.

## Links
- **Live app:** https://main.d6f34l6r9rpi9.amplifyapp.com
- **Bad-air day (recorded, 19 Nov 2025):** https://main.d6f34l6r9rpi9.amplifyapp.com/?replay=delhi-nov
- **API health:** https://qcx2qrt6bj.execute-api.us-east-1.amazonaws.com/api/health
- **Code:** https://github.com/arnavgupta2004/Saans
- **Demo video:** https://youtu.be/X5oNj2PFbpo
- **AWS Builder Center blog:** `<BLOG_URL>`
