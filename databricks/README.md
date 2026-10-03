# Databricks pipeline

Runs the wound-infection model on Databricks: Delta tables, MLflow tracking, a Unity Catalog
model, a Model Serving endpoint, and batch scoring for a dashboard.

```
download / upload glucose ─► 01_ingest ─► readings_bronze, demo_readings_bronze
                                   │
                                   ▼
                          02_train_mlflow ─► features_silver
                                   │         MLflow experiment (CV metrics per fold)
                                   ▼
                     Unity Catalog model  <catalog>.<schema>.wound_infection_risk @champion
                          │                         │
                          ▼                         ▼
                     03_serve                 04_batch_score ─► risk_scores_gold, treatment_plan_gold
                  (REST endpoint)                    │
                                                     ▼
                                05_live_demo ─► live_risk_gold ─► dashboard (dashboard_queries.sql)
```

## Setup

1. **Clone the repo into Databricks**: Workspace → Create → **Git folder** →
   `https://github.com/suhaant/WolfHacks`, branch `adam`.
   The notebooks import the project's Python files from the repo root.
2. Open `databricks/01_ingest` and set the widgets at the top:
   - `catalog`: `workspace` (Free Edition default) or any catalog you can write to
   - `schema`: `wolfhacks`
3. Run the notebooks in order, on **serverless** compute.

| Notebook | What it does | Run time |
|---|---|---|
| `01_ingest` | Creates schema + `raw` volume, gets glucose data, simulates 600 training + 20 demo wounds → Bronze tables | ~3 min |
| `02_train_mlflow` | Silver features, leave-one-person-out CV logged to MLflow, demo check, final model registered to Unity Catalog as `@champion` | ~5–10 min |
| `03_serve` | Model Serving endpoint (scale-to-zero) + test query | ~10–20 min to start |
| `04_batch_score` | Scores a readings table → `risk_scores_gold` + `treatment_plan_gold` | ~1 min |
| `05_live_demo` | Replays DEMO-02 a few hours at a time to show risk climbing live | ~2 min |

**Glucose data on Free Edition:** outbound internet is restricted, so the PhysioNet download in
`01_ingest` may fail. If it does, run `./download_glucose.sh` on your laptop and upload the
`data/bigideas` folder to **Catalog → `<catalog>` → `<schema>` → Volumes → `raw` → `bigideas/`**.

**Model Serving** may not be available on every plan (check Free Edition). Everything except
`03_serve` works without it, and `predict.py` can serve the API elsewhere.

## Tables

| Layer | Table | Contents |
|---|---|---|
| Bronze | `readings_bronze` | 403,200 simulated training readings with labels |
| Bronze | `demo_readings_bronze` | 20 held-out demo wounds (participants 14–16), no labels |
| Bronze | `demo_answer_key` | demo labels (grading only) |
| Bronze | `glucose_participants` | 16 real CGM participants |
| Silver | `features_silver` | 27 trend features per reading |
| Gold | `risk_scores_gold` | `p_infected`, `risk_score` (0–100), `tier` per reading |
| Gold | `treatment_plan_gold` | latest risk + next LED / ultrasound session per wound |
| Gold | `live_risk_gold` | live demo output |

## The registered model

`wound_risk_pyfunc.py` wraps `predict.WoundRiskModel` as an MLflow pyfunc, so the model in Unity
Catalog takes **raw readings** (a wound's full history) and does the feature engineering itself.

Input columns: `wound_id, timestamp, ph, temp_c, impedance_kohm, blood_glucose_mgdl, wound_glucose_mM`
Output columns: `wound_id, timestamp, hour, p_infected, predicted_label, risk_score, tier, tier_name`

```python
import mlflow
mlflow.set_registry_uri("databricks-uc")
model = mlflow.pyfunc.load_model("models:/workspace.wolfhacks.wound_infection_risk@champion")
risk = model.predict(readings_df)
```

## Scheduling batch scoring

Workflows → Create job → task type **Notebook** → `databricks/04_batch_score`, serverless,
parameters `catalog`, `schema`, `source_table` (e.g. the table your app writes readings to),
trigger **every 30 minutes**.

## Dashboard

Dashboards → Create dashboard → add datasets from `dashboard_queries.sql`:
risk over time per wound (line), current status table, wounds needing attention (counter),
live demo (line), predicted vs true labels on the demo set (bar).
