# WolfHacks: Wound Infection Agent

A Claude Opus agent that takes one wound-sensor reading, asks an infection model for a
probability, and works out a violet-light and 20–40 kHz ultrasound treatment plan.

```
sensor reading ──► Opus agent ──tool──► get_sensor_reading
                       │       ──tool──► predict_infection   (ML model → probability)
                       │       ──tool──► plan_treatment      (probability → dose)
                       ▼
                 Assessment JSON  (numbers from tools + the agent's reasoning/flags)
```

The agent never makes up the probability or the dose. Those come from the model and the
deterministic planner. The agent checks data quality, points out signals that disagree,
explains the result and says when a clinician should review it.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env           # then paste your key after ANTHROPIC_API_KEY=
```

## Run

```bash
python main.py -v                                   # dummy "infected" reading
python main.py --scenario healthy --seed 1          # healthy | early_infection | infected | noisy_sensor
python main.py --reading sample_data/reading_example.json
python main.py --offline                            # no LLM, no API key needed
python main.py --out output/assessment.json
python -m pytest
```

## Replacing placeholders with real things

| What | Where | How |
|---|---|---|
| Sensor data | `wound_agent/data_sources.py` | Pass `--reading file.json` (same shape as `sample_data/reading_example.json`), or add a class with `get_reading(patient_id)` and return it from `get_data_source()` |
| ML model | `wound_agent/model.py` | Set `INFECTION_MODEL_PATH=model.joblib` for an sklearn model (check `FEATURE_ORDER`), or add a class with `predict_proba(reading)` and return it from `load_model()` |
| Infection threshold | `model.py` → `INFECTION_THRESHOLD` | Set it from the model's validation results |
| Doses | `wound_agent/treatment.py` → `TREATMENT_BANDS`, `MAX_*` | **Every value is a placeholder.** Replace with clinically sourced values |
| Dummy ranges | `data_sources.py` → `SCENARIOS` | Only used for demos and tests |
