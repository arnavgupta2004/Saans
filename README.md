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
