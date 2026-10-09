# Saans

Saans turns hour-by-hour air-quality forecasts into deterministic, school-timetable safety decisions.

```bash
cd backend
.venv/bin/uvicorn app:app --reload
curl http://localhost:8000/api/health
curl http://localhost:8000/api/schools
curl http://localhost:8000/api/schools/delhi-anand-vihar
curl 'http://localhost:8000/api/schools/delhi-anand-vihar/today'
curl 'http://localhost:8000/api/schools/delhi-anand-vihar/week'
curl 'http://localhost:8000/api/schools/delhi-anand-vihar/best-day?start=09:00&end=12:00'
curl 'http://localhost:8000/api/schools/delhi-anand-vihar/notice?lang=en&polish=false'
curl -X POST http://localhost:8000/api/ask -H 'Content-Type: application/json' -d '{"school_id":"delhi-anand-vihar","question":"What is today’s plan?","lang":"en"}'
```

To create or replace a school, `POST` the `School` JSON returned by `/api/schools` to `/api/schools`.

## Data sources

CPCB via data.gov.in is preferred; when unreachable from AWS, Saans calibrates with CPCB station data via OpenAQ. The assistant is built with Strands Agents (AWS open source); Bedrock Nova Lite is supported, Gemini is used because our account's Bedrock access was blocked.

- Forecast: Open-Meteo Air Quality API (hourly PM2.5/PM10).
- Calibration chain: data.gov.in CPCB → OpenAQ v3 (nearest PM2.5 sensor ≤ 25 km, < 2 h old) → uncalibrated. `sources.observation` says which was used (e.g. `live:openaq`).
- Replay: `/api/schools/{id}/today?replay=delhi-nov` serves a recorded Delhi day (19 Nov 2025), clearly labelled.

## Agent

Select the model with `MODEL_PROVIDER=bedrock|gemini`. Model ids come only from SAM parameters (`BedrockModelId`, `GeminiModelId`); Gemini needs `GEMINI_API_KEY`. Safety decisions always come from deterministic `rules.py`; the model only explains, and if it fails the API logs the exception and returns a deterministic fallback.
