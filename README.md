# WolfHacks: Smart Wound Patch

Two parts:

1. **Infection-detection ML** (Adam): an XGBoost model trained on simulated patch data
   that turns pH, temperature, moisture (impedance) and glucose readings into a 0–100
   infection risk score, and `risk_to_dose.py`, which turns that into a 405 nm LED /
   40 kHz + 1.5 MHz ultrasound plan. Details below.
2. **Opus agent** (`wound_agent/`): a Claude Opus agent that runs the model and the
   dosing as tools, then judges the evidence: trends against the patient's baseline,
   sensor faults, conflicting signals, and whether a clinician should review.

## Agent

```
wound history ──► Opus agent ──tool──► get_sensor_history  (summary vs. day-1 baseline)
                      │       ──tool──► predict_infection   (XGBoost → risk score, tier)
                      │       ──tool──► plan_treatment      (risk_to_dose → session plan)
                      ▼
                Assessment JSON  (numbers from tools + the agent's notes)
```

The agent never makes up the risk or the dose. `caveats` in the output are generated in
code; `agent_notes` is the only part Opus writes.

### Setup (Python 3.12+)

```bash
python -m venv .venv && .venv/Scripts/activate      # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env                                # paste ANTHROPIC_API_KEY (and workspace ID if needed)
```

### Run

```bash
python main.py -v                                   # dummy "infected" wound
python main.py --scenario early_infection --seed 1  # healthy | early_infection | infected | sensor_fault | patch_lifted
python main.py --history sample_data/simulated_wound_history.csv
python main.py --offline                            # no LLM, no API key needed
python main.py --out output/assessment.json
python -m pytest
```

Dummy wounds come from Adam's simulator (`generate_data.simulate_wound`) with a synthetic
glucose trace, so no PhysioNet download is needed. The simulator's answer key is
stripped before the agent sees the data.

### Using real data

Pass `--history file.csv` (or `.json`) in the format `predict.py` reads: one row every
30 min from when the patch went on, columns `timestamp`, `ph`, `temp_c`,
`impedance_kohm`, `blood_glucose_mgdl`, `wound_glucose_mM` (optionally `wound_id`). At
least 24 h is needed; the first day sets the patient's baseline. For a live feed, add a
class with `get_history(wound_id)` in `wound_agent/data_sources.py`.

---

# Smart Wound Patch — Infection Detection ML

Machine-learning pipeline that predicts bacterial wound infection from a smart patch's
**pH, temperature, and moisture (impedance)** sensors, optionally with **blood glucose**
(CGM) and **wound-fluid glucose**. It outputs a 0–100 infection risk score, which sets
the dose of the 405 nm LED and the 40 kHz / 1.5 MHz ultrasound.

> **Proof of concept.** No public dataset of continuous wound sensor readings with
> infection labels exists, so training data is **simulated** from 30+ published studies
> plus **real Dexcom glucose data** from 16 people. Retrain on real patch data before any
> clinical use. Dosing values are prototype settings, not a validated medical protocol.

## Quick start

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
./run_all.sh
```

macOS + XGBoost: if `import xgboost` fails with `libomp.dylib`, run `brew install libomp`.

## Files

| File | What it does |
|---|---|
| `download_glucose.sh` | Downloads real CGM data (16 people, ~3 MB) from PhysioNet |
| `glucose_data.py` | Loads Dexcom traces, splits into whole days, resamples to 30 min |
| `generate_data.py` | **Simulator.** 600 wounds × 14 days × every 30 min = 403,200 labeled readings. All biology parameters in the `P` dict, with sources |
| `train_model.py` | Feature engineering (`add_features`) + 4-fold person-grouped CV comparing sensor sets |
| `train_final.py` | Leave-one-person-out CV (16 folds), sensor ablation, isotonic calibration, final model |
| `compare_models.py` | Random forest vs XGBoost, same features and CV |
| `make_demo.py` | Held-out demo/API test set (3 people removed from training, new seed) |
| `risk_to_dose.py` | Probability → smoothed risk score → tier → LED / ultrasound session plan |
| `build_workbook.py` | Excel summary of research values, data, and results |
| `research/*.md` | Extracted literature values for pH, temperature, moisture, with sources |

## Data

**Simulated wounds** (`generate_data.py`):
- 50% acute / 50% chronic. ~35% infected (odds × 1.07 per +10 mg/dL mean glucose); otherwise 70% healing / 30% stalled
- Infection onset at a random time on day 2–11, 6–24 h sensor lag, S-curve rise peaking in 2–4 days
- Noise: day/night temperature cycle, showers, dressing changes, pH drift, patch peel-off, sensor noise
- Labels from the true hidden state: `normal`, `warning` (first 24 h after onset), `infection` (>24 h)

**Real glucose**: BIG IDEAs Lab Glycemic Variability and Wearable Device Data v1.1.3,
PhysioNet, ODC-By 1.0 — https://physionet.org/content/big-ideas-glycemic-wearable/1.1.3/
(16 adults, HbA1c 5.2–6.4%, Dexcom G6, ~8–10 days).

### Simulator parameters (`generate_data.py`, `P` dict)

| Parameter | Value | Basis |
|---|---|---|
| `ph_base` | acute 6.6 ± 0.45, chronic 7.0 ± 0.45 | Sci Rep 2026 cohort: 6.59 / 7.11 |
| `ph_slope_per_day` | healing −0.088/wk, stalled −0.03/wk | Sci Rep 2026 |
| `ph_infection_rise` | +0.65 ± 0.25 | infected 7.53 vs non-infected 6.90 |
| `ph_nonresponder_frac` | 0.15 | assumption (horse model: no pH effect; necrosis lowers pH) |
| `ph_staph_dip` | 0.3 | in vitro *S. aureus* early acidification |
| `ph_noise` / `ph_drift_per_h` | 0.05 / 0.01 | assumption (meters ±0.1–0.2; bench drift ≤0.04/h) |
| `temp_base` | 33.5 ± 0.8 °C | covered skin |
| `temp_slope_per_day` | healing −0.19/wk, stalled −0.09/wk | Sci Rep 2026 |
| `temp_infection_rise` | +1.6 ± 0.6 °C | Fierheller 1.1, SIDESTEP 1.6, 2.15 °C cutoff |
| `temp_circadian_half_amp` | 0.3–0.7 °C, peak 03:00 | wrist 1.2–1.4 °C p-p, damped (assumption) |
| `temp_noise` | 0.1 °C | MAX30205 datasheet |
| `shower_temp_drop` / `shower_prob_per_day` | 3.5 °C / 0.7 | sensor demo / assumption |
| `z_base` | acute 8 ± 2, chronic 12 ± 4 kΩ @1 kHz | Kekonen 2019: fresh wound 6.3 kΩ |
| `z_log_growth_per_day` | healing 0.06, stalled 0.01 | assumption (direction published) |
| `z_infection_drop` | 35% ± 12% | assumption (direction published) |
| `z_noise_frac` / `z_shower_frac` | 5% / −40% | assumption |
| `lag_h` / `time_to_peak_h` | 6–24 h / 48–96 h | rat, pig, rabbit models |
| `dressing_change_h` | 48–72 h | Milne 2016 |
| `detach_prob_per_wound` / `detach_duration_h` | 0.1 / 3–12 h | assumption |
| `frac_chronic` / `frac_infected` / `frac_stalled_of_uninfected` | 0.5 / 0.35 / 0.3 | design |
| `staph_frac_of_infected` | 0.55 | Sci Rep 2026 cultures (6/11) |
| `glucose_or_per_10` | 1.07 | SCOAP surgical infection OR |
| `blood_glucose_rise` | +8 ± 4 mg/dL | +4 non-diabetic to +15–20 T1D |
| `glucose_spike_amplify` | 0.15 | CV 37.3 → 39.6% during infection |
| `wound_glucose_lag_h` | 4 h | Gao lab 2023 |
| `wound_serum_ratio` | 0.5–0.8 | assumption (wound < serum, Trengove 1996) |
| `wound_glucose_drop` | 40% ± 10% | Gao lab 2023: >35% drop |

Run settings: `--wounds 600 --days 14 --step-min 30 --seed 42`.

## Features (27)

For each sensor (`ph`, `temp_c`, `log_z` = log impedance, `blood_glucose_mgdl`,
`wound_glucose_mM`), using **past readings only**:

| Feature | Definition |
|---|---|
| `_sm` | 6 h rolling median |
| `_vs_base` | `_sm` minus the patient's own day-1 median |
| `_d6h` / `_d24h` | change in `_sm` over 6 h / 24 h |
| `_std24h` | 24 h rolling standard deviation |

Plus `tod_sin`, `tod_cos` (time of day). The first 24 h of each wound is used for the
baseline and is not scored.

## Models

| | Random forest | XGBoost |
|---|---|---|
| Library | scikit-learn `RandomForestClassifier` | `xgboost.XGBClassifier` |
| Trees | `n_estimators=150` | `n_estimators=300` |
| Depth | `max_depth=14` | `max_depth=6` |
| Other | `min_samples_leaf=20` | `learning_rate=0.1, subsample=0.8, colsample_bytree=0.8, min_child_weight=5, objective="multi:softprob", tree_method="hist"` |
| Calibration | `CalibratedClassifierCV(method="isotonic")`, person-grouped folds | — |

Classes: `normal`, `warning`, `infection`. Infection probability = P(warning) + P(infection).

## Validation

- **Leave-one-person-out** (16 folds, `LeaveOneGroupOut` on `participant_id`): each person
  is tested by a model that never saw their data
- 4-fold `GroupKFold` for sensor ablation and calibration
- Wound-level alarm = 4 h of consecutive warning/infection predictions

## Results (simulated data)

| | Random forest | XGBoost |
|---|---|---|
| AUC | 0.976 | 0.978 |
| Brier skill score (R² equivalent) | 0.834 | 0.845 |
| Infected wounds detected | 100% | 100% |
| Median hours from onset to alarm | 30.3 | 27.2 |
| False alarms, clean wounds | 0.3% | 2.1% |
| Model size / per-prediction time | 11.9 MB / 12.4 ms | 3.1 MB / 0.14 ms |

Sensor ablation (AUC): pH 0.917 · temperature 0.933 · moisture 0.952 · wound glucose 0.886 ·
blood glucose 0.650 · **pH + temp + moisture 0.976** · all five 0.975.

Scores are optimistic because the model is tested on the same simulator it learned from.

## Risk score → treatment (`risk_to_dose.py`)

- `risk = 100 × EMA(P(infected), tau = 3 h)`; tiers with 10-point hysteresis:
  monitor (<30) · watch (≥30) · treat (≥55) · intensive (≥80)
- 3 sessions/day. 405 nm LED at 10 mW/cm², dose scaled with risk, **cap 36 J/cm²/day**
- 40 kHz ultrasound, 4–10 min at 0.1–0.5 W/cm² (tier ≥2), run before the LED
- 1.5 MHz ultrasound, 30 mW/cm², 20% duty, 20 min/day (monitor tier only)
- Interlock: no treatment while impedance > 150 kΩ (patch lifted)

## Using the trained model (`predict.py`)

The trained XGBoost model is in `model/`:
- `xgboost_model.json` — model in XGBoost's portable JSON format (4.4 MB)
- `model_meta.json` — feature order, class labels, training settings

It was trained on all 600 simulated wounds (all 16 glucose participants).

```bash
python predict.py readings.csv --out risk.csv    # or readings.json
```

```python
from predict import WoundRiskModel
model = WoundRiskModel()
result = model.predict(readings_df)   # per reading: p_infected, risk_score (0-100), tier
plan = model.latest_plan(result)      # per wound: LED / ultrasound plan for the next session
```

Input columns: `wound_id`, `timestamp` (or `hour`), `ph`, `temp_c`, `impedance_kohm`,
`blood_glucose_mgdl`, `wound_glucose_mM`, one row every 30 min. Send each wound's full
history: the first 24 h set the patient's baseline (no risk returned for them) and the
features use 6 h and 24 h trends.
