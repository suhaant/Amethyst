# Databricks care record

Databricks holds two things for PulsePatch:

1. **The cloud record.** Every patch reading and every assessment, in two tables.
2. **The care-team view.** A dashboard of all monitored wounds, which need attention, and what the agent concluded.

Everything stored is simulated. Do not put real patient data in this workspace.

```
patch_gateway.py ──► readings ──► main.py --databricks ──► assessments ──► dashboard
(stands in for the   (Databricks)  (model + agent,          (Databricks)    (Databricks)
 phone forwarding                   run locally)
 patch readings)
```

It is opt-in. Without `--databricks`, `main.py` behaves exactly as before and imports no Databricks code, so `--scenario`, `--history` and `--offline` remain the fallback if the workspace is unavailable.

## Setup

1. In the Databricks workspace, start (or create) a **SQL warehouse** and copy its ID from the warehouse's connection details.
2. Create a **personal access token** in your user settings.
3. Add these to `.env` in the repo root (see `.env.example`):

| Setting | Required | Default |
|---|---|---|
| `DATABRICKS_HOST` | yes | none (for example `https://dbc-xxxx.cloud.databricks.com`) |
| `DATABRICKS_TOKEN` | yes | none |
| `DATABRICKS_WAREHOUSE_ID` | yes | none |
| `DATABRICKS_CATALOG` | no | `workspace` |
| `DATABRICKS_SCHEMA` | no | `pulsepatch` |

4. `pip install -r requirements.txt` (adds `databricks-sdk`).

No separate table setup is needed: the gateway creates the schema and both tables on first run.

## Demo run sheet

```bash
python patch_gateway.py --demo-cohort          # five wounds, one per simulator scenario
python main.py --databricks --all              # assess each one, save the assessments
# open the dashboard: five wounds ranked by risk, with the agent's summaries

# live: a sixth wound arrives
python patch_gateway.py --wound wound-006 --scenario infected --seed 2
python main.py --databricks --wound wound-006 -v
# refresh the dashboard
```

Add `--offline` to `main.py` to skip the LLM (no Anthropic key needed); those rows are stored with `assessed_by = model-only`.

A cold warehouse can take a minute or two to start. The store waits up to two minutes per statement before giving up.

## Tables

`readings` has one row per 30-minute reading, with the same column names and units `predict.py` reads, plus `source` (`simulated`, `file` or `patch`) and `ingested_at`. Uploading a wound again replaces its rows.

`assessments` is append-only, one row per run: the risk score, tier, dose plan, the agent's notes, the caveats, and the full assessment as JSON. Repeated runs build a risk history.

The exact columns are in `wound_agent/databricks_store.py`.

## Building the dashboard

The dashboard is built by hand from the four queries in `dashboard.sql`. Menu names below are from memory of the Databricks UI and may differ slightly in your workspace.

1. In the sidebar open **Dashboards** and create a new dashboard. Name it "PulsePatch care team (simulated data)".
2. On the **Data** tab, create four datasets with **Create from SQL**, pasting one query from `dashboard.sql` into each.
3. On the canvas add:
   - a **counter** on dataset 1, value `wounds_needing_attention`;
   - a **table** on dataset 2;
   - three **line charts** on dataset 3 with `timestamp` on the x-axis and `ph`, `temp_c`, `impedance_kohm` on the y-axis, coloured by `wound_id`;
   - a **line chart** on dataset 4 with `generated_at` on the x-axis, `risk_score` on the y-axis, coloured by `wound_id`.
4. Add a **filter** widget on `wound_id` and connect it to datasets 3 and 4.
5. Publish.

## Tests

```bash
python -m pytest tests/test_databricks_store.py    # fake warehouse, no network
python -m pytest tests/test_databricks_live.py     # real round trip; skipped unless the settings above are present
```

The live test writes one short wound under a throwaway id and deletes it afterwards.

## Not included

- Training, experiment tracking or model serving on Databricks.
- The app reading from Databricks.
- A real patch feed. The firmware now reports pH, temperature and impedance in the model's units, but not the two glucose columns, so `source = patch` is reserved until those are joined in from the glucose dataset.
