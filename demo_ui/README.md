# Amethyst live demo UI

Split-screen demo for after the pitch. No hardware yet, so the presenter types patch
readings on the left; the right side shows the pipeline running for real:

patch reading → agent → XGBoost model → therapy plan → app

```bash
pip install -r requirements.txt
python demo_ui/server.py            # open http://localhost:8000
python demo_ui/server.py --offline  # never call Claude
```

- **Scenarios**: Healthy, Early infection, Infection, Patch lifted, Sensor fault fill the inputs.
- **Advance time**: each reading is streamed into the patch history over 30 min to 24 h
  (the model scores trends, so time has to pass). The first 24 h are a healthy baseline.
- **Agent**: `wound_agent.run_assessment` (an LLM with the model and dosing as tools)
  writes the assessment. With `OPENROUTER_API_KEY` in `.env` it uses Gemini 3.8 Flash
  through OpenRouter (~13 s, ~$0.005 per assessment). `GEMINI_API_KEY` uses Google
  directly (free tier, ~5 requests/min) and `ANTHROPIC_API_KEY` uses Claude Opus;
  `AGENT_PROVIDER=openrouter|gemini|claude` picks one when several are set. Without a key, the same model and
  dosing run and a rule-based summary stands in. Click the header chip to switch.
- **App**: `GET /api/state` returns the latest risk, tier, therapy plan and agent notes for
  the Expo app to poll.
- **Reset** (header button) starts a new patient.

## Hardware API

The patch (or any script, curl or Postman) can send readings instead of typing them in:

```bash
curl -X POST http://localhost:8000/api/readings \
  -H 'Content-Type: application/json' \
  -d '{"ph": 7.3, "temp_c": 35.1, "impedance_kohm": 6.5, "blood_glucose_mgdl": 112, "wound_glucose_mM": 2.5}'
```

Each reading stands for 30 minutes of patch data (`advance_hours`, default 0.5) and runs
with offline rules unless `"use_agent": true`. The response has `risk_score`, `tier`,
`level`, `therapy` and the full `treatment` plan. The demo UI animates the reading live
(tagged **API** in the log) and the Expo app picks it up within a second.

Pretend to be the patch with the helper script:

```bash
python demo_ui/send_reading.py --scenario infection --count 8 --every 3
```

| Endpoint | What |
| --- | --- |
| `POST /api/readings` | Hardware API: one reading in, risk + therapy plan out |
| `GET /api/state` | Latest assessment (the Expo app polls this) |
| `GET /api/events` | Server-sent events for every pipeline step (the demo UI listens) |
| `POST /api/reset` | New patient with a fresh 24 h baseline |
| `GET /docs` | Interactive API docs (FastAPI) |
