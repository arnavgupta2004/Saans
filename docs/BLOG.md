# Saans: turning an hourly AQI forecast into a school timetable

*Team Chernobyl · Environmental Hacks (WeMakeDevs × AWS, Bharat Builds Tour) · Track 01: Air*

## The problem

Every winter in North India, the conversation about schools and air quality swings between two settings: "normal day" and "school closed". On 17 November 2024, Delhi's AQI reached 441, GRAP Stage IV was invoked, and physical classes across Delhi-NCR were suspended. But most bad days are not closure days. They are days when the air at 08:40 is Very Poor and the air at 13:40 is merely Moderate — and nobody tells the PE teacher.

Children are the most exposed. WHO's 2018 report on air pollution and child health found that 93% of the world's children live with air pollution above WHO guideline levels. A 2024 *Lancet Planetary Health* study across ten Indian cities found that short-term rises in PM2.5 are associated with higher daily mortality, even at levels below India's own standard. Exposure is not just a yearly number; it is an hourly one.

Saans ("breath") asks a narrow question: *given this school's actual timetable, what should change today?*

## The design

We split the product into two halves that never mix.

**The deterministic half decides.** A planner pulls the hourly PM2.5/PM10 forecast for the school's coordinates from Open-Meteo (CAMS model), converts it to India's National AQI using CPCB breakpoints, and runs every outdoor period through a rules table: high-intensity PE in Poor air goes indoors; assembly in Very Poor air moves to the PA system; students with asthma get a stricter column of their own. If a period must not run outdoors, the planner looks for an indoor class later that day whose hour has cleaner air, and suggests an *exchange*: "Class 7B PE 08:40 ⇄ Period 8 13:40 · AQI 351 → 127". Every rules cell has a test.

**The language half explains.** A Strands agent answers questions like "Is PE at 8:40 safe?" by calling the same planner as tools. It is not allowed to decide anything. After it answers, a *number guard* checks that every number of 20 or more in the reply appears in that request's tool outputs. If the model invents an AQI, the user gets the deterministic plan summary instead. The UI only shows "✓ numbers checked" when the check passed.

Around them: a bilingual parent notice with a WhatsApp link, a best-day finder, and labels saying where every number came from — live, cached, sample, or a recorded replay day.

## The stack

- **AWS Lambda + Amazon API Gateway:** FastAPI behind Mangum; pay-per-request fits spiky school mornings.
- **Amazon DynamoDB:** school profiles, plus a cache of precomputed daily plans keyed `school_id#date`.
- **Amazon EventBridge Scheduler:** a second Lambda at 06:00 `Asia/Kolkata`, so the plan is ready before school.
- **Amazon CloudWatch + Amazon SNS:** error alarms that email us.
- **AWS Amplify Hosting:** the React frontend, rebuilt on every push.
- **AWS SAM:** the backend as one template; keys as NoEcho parameters.
- **Strands Agents:** the agent framework, and why swapping models was a config change.

## What fought back

**data.gov.in refused AWS.** Our plan was to calibrate the forecast with the nearest live CPCB reading from data.gov.in. From Lambda, every call failed with `Connection refused`. We added a 3-second connect timeout so it never slows the page, then a second source: OpenAQ. Our first OpenAQ version happily picked a low-cost sensor called "Air Check" 8 km away — not what we promised in the README. We restricted it to reference monitors, preferring CPCB. Then a probe script showed the real story: OpenAQ's CPCB feed was about 50 hours behind. Calibrating today's hourly forecast with a two-day-old reading would make it *worse*, so Saans now runs uncalibrated and says exactly why on screen.

**Bedrock was blocked on our account.** Strands made this survivable: the agent is model-agnostic, so `MODEL_PROVIDER=gemini` swapped Amazon Bedrock for Gemini without touching the tools. Bedrock Nova Lite is still a supported provider in the code.

**The AQI band-gap bug.** The published NAQI breakpoints have integer gaps — PM2.5 Satisfactory ends at 60, Moderate starts at 61. Forecasts are decimals. A value of 60.1 fell through every band and our code returned AQI 500, "Severe". We found it in the first live output, made the bands contiguous, clamped each sub-index to its band's top, and added tests for 60.9, 100.5 and 250.5.

**Swap semantics.** Our first swap rule moved PE into *another outdoor slot*, sometimes the same slot twice, and suggested moving assembly — which cannot move. The parent notice even said "moved to 09:20" for an optional suggestion. We rewrote it as an exchange with indoor classes, one target per slot, worst period first, and made the notice offer changes instead of announcing them.

**Gemini latency.** Under load, the larger Gemini model took about 18 seconds just to return "503: high demand", and API Gateway cuts requests at 30 seconds. We disabled the framework's own retries (6 attempts from 4 seconds), added a budget-aware chain — retry briefly, fall back to a lighter model, then fall back to the plan summary — and learned that Gemini rejects request deadlines under 10 seconds. Moving the primary to a flash-lite model took typical answers from ~20 s to ~3 s.

**The browser is not curl.** Every curl check of Ask passed. In the browser, Ask never worked from the hosted site: API Gateway forwarded the CORS preflight to FastAPI, which only allowed `localhost`. Playwright screenshots of the deployed app caught it.

## What's next

- A small fetcher outside AWS that pulls fresh CPCB readings into the cache, so calibration works again.
- Per-school timetables entered by teachers, with "apply swap" writing back to the timetable.
- Validating the school thresholds with paediatricians and running a pilot with a few Delhi schools this winter.

Saans will not clean the air. It tries to make sure that, on a bad morning, the children who are outside are outside during the cleaner hours.

*Live: https://main.d6f34l6r9rpi9.amplifyapp.com · Code and sources: see the README.*
