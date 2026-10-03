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
- **Agent**: with `ANTHROPIC_API_KEY` in `.env`, `wound_agent.run_assessment` (Claude Opus with
  the model and dosing as tools) writes the assessment. Without a key, the same model and
  dosing run and a rule-based summary stands in. Click the header chip to switch.
- **App**: `GET /api/state` returns the latest risk, tier, therapy plan and agent notes for
  the Expo app to poll.
- **Reset** (header button) starts a new patient.
