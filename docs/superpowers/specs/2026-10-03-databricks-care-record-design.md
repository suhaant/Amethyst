# Databricks care record: design

Date: 2026-10-03
Branch: `databricks` (off `agent-reasoning`)
Status: approved in conversation, awaiting written-spec review

## Goal

Make Databricks a working part of PulsePatch without changing the current design.

Databricks becomes two things the product description promises but nobody has built:

1. **The cloud record.** Every patch reading and every assessment is stored there.
2. **The care-team view.** A dashboard shows a clinician all monitored wounds, which need
   attention, and what the agent concluded.

Success means the live demo can show: readings arrive in Databricks, the agent reads them
and assesses the wound, and the dashboard updates.

## Constraints

- **Small and certain to work.** An earlier Databricks pipeline (five notebooks covering
  ingestion, training, serving and scoring) was reverted for being too much and too likely
  to fail. This design uses only a SQL warehouse, two tables and one dashboard.
- **No change to the existing design.** The model, training scripts, `risk_to_dose.py`, the
  agent's prompt, tools and schemas, the app and the firmware are untouched.
- **Opt-in.** Without the new `--databricks` flag, behaviour is identical to today and no
  Databricks code is imported. The existing `--scenario`, `--history` and `--offline` paths
  are the fallback if the workspace is unavailable during a demo.

## How it fits

```
patch_gateway.py ──► readings ──► main.py --databricks ──► assessments ──► dashboard
(stands in for the   (Databricks)  (model + Opus agent,     (Databricks)    (Databricks)
 phone forwarding                   run locally as now)
 patch readings)
```

The agent already defines where a wound's history comes from: the `DataSource` protocol in
`wound_agent/data_sources.py` (`get_history(wound_id) -> DataFrame` plus an `is_dummy`
attribute). The README names this as the place to add a live feed. The Databricks store
implements that protocol, so the agent, model and dosing code need no changes.

## Components

### `wound_agent/databricks_store.py` (new)

One class, `DatabricksStore`, with one job: move readings and assessments between pandas
and two Databricks tables.

| Member | Behaviour |
|---|---|
| `DatabricksStore.from_env()` | Builds a store from environment settings. Raises `DatabricksConfigError` naming every missing setting. |
| `ensure_tables()` | Creates the schema and both tables if they do not exist. |
| `upload_readings(history, source)` | Replaces the stored readings for the wound ids in `history`, then inserts the new rows. Returns the row count. Replacing makes re-runs safe. |
| `list_wounds()` | Returns the distinct wound ids in `readings`, sorted. |
| `get_history(wound_id)` | Returns the wound's readings as a DataFrame with `wound_id`, `timestamp`, `hour` and the five sensor columns, sorted by `hour`. Raises `ValueError` if the wound has no readings. Sets `is_dummy`. |
| `save_assessment(assessment)` | Appends one row to `assessments`. |
| `is_dummy` | `True` when the last fetched history contains any `simulated` reading, so the existing "Readings are simulated dummy data" caveat stays accurate. |

The store talks to Databricks through one injectable function,
`execute(sql, params) -> list[dict]`. The default uses the Databricks SDK's SQL Statement
Execution API and polls until the statement finishes, allowing up to two minutes for a
cold warehouse. Tests pass a fake `execute`, so they need no network.

`databricks.sdk` is imported inside the default `execute`, not at module import, so the
SDK is only needed when `--databricks` is used.

A pure helper, `assessment_row(assessment) -> dict`, flattens an `Assessment` into the
`assessments` columns. List fields are joined with `"; "`. `assessed_by` is `opus-agent`
when `agent_notes` is present and `model-only` otherwise.

### `patch_gateway.py` (new)

Stands in for the phone or gateway that forwards patch readings to the cloud. It takes any
existing data source and uploads its history.

```
python patch_gateway.py --demo-cohort
python patch_gateway.py --wound wound-006 --scenario infected --seed 2
python patch_gateway.py --wound wound-007 --history sample_data/simulated_wound_history.csv
```

- `--demo-cohort` uploads five wounds, one per existing scenario, with seed 0:
  `wound-001` healthy, `wound-002` early_infection, `wound-003` infected,
  `wound-004` sensor_fault, `wound-005` patch_lifted.
- Readings from the simulator are stored with `source = simulated`; readings from
  `--history` with `source = file`. `patch` is reserved for a real device feed.
- It calls `ensure_tables()` first, so no separate setup step is needed.

### `main.py` (two flags)

- `--databricks`: read history from Databricks and save each assessment back. Mutually
  exclusive with `--history`; `--scenario` and `--seed` are ignored when it is set.
- `--all`: assess every wound in `readings`. Requires `--databricks`; cannot be combined
  with `--out`.

The assessment is printed before it is saved, so a failed save never loses the result.

### `databricks/dashboard.sql` and `databricks/README.md` (new)

Four dashboard queries and click-by-click steps for building the dashboard in the
Databricks UI, plus the setup steps and the demo run sheet. The dashboard is built by hand
rather than generated through the API, because the generated format is easy to get subtly
wrong and hard to verify.

### `requirements.txt` and `.env.example`

- `requirements.txt` adds `databricks-sdk`.
- `.env.example` adds the settings below. `.env` is already git-ignored.

| Setting | Required | Default |
|---|---|---|
| `DATABRICKS_HOST` | yes | none |
| `DATABRICKS_TOKEN` | yes | none |
| `DATABRICKS_WAREHOUSE_ID` | yes | none |
| `DATABRICKS_CATALOG` | no | `workspace` |
| `DATABRICKS_SCHEMA` | no | `pulsepatch` |

## Tables

```sql
CREATE TABLE IF NOT EXISTS <catalog>.<schema>.readings (
  wound_id            STRING    NOT NULL,
  `timestamp`         TIMESTAMP NOT NULL,
  hour                DOUBLE    NOT NULL,   -- hours since the patch was applied
  ph                  DOUBLE,
  temp_c              DOUBLE,
  impedance_kohm      DOUBLE,
  blood_glucose_mgdl  DOUBLE,
  wound_glucose_mM    DOUBLE,
  source              STRING    NOT NULL,   -- simulated | file | patch
  ingested_at         TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS <catalog>.<schema>.assessments (
  wound_id                    STRING    NOT NULL,
  generated_at                TIMESTAMP NOT NULL,
  assessed_by                 STRING    NOT NULL,   -- opus-agent | model-only
  n_readings                  INT,
  history_hours               DOUBLE,
  risk_score                  DOUBLE,
  p_infected                  DOUBLE,
  predicted_label             STRING,
  tier                        STRING,
  risk_score_6h_ago           DOUBLE,
  risk_score_24h_ago          DOUBLE,
  led_dose_j_cm2              DOUBLE,
  led_405nm_min               DOUBLE,
  us_40khz_min                DOUBLE,
  us_1p5mhz_min               DOUBLE,
  skipped_reason              STRING,
  summary                     STRING,
  trend                       STRING,
  reasoning                   STRING,
  data_quality_flags          STRING,
  conflicting_signals         STRING,
  recommend_clinician_review  BOOLEAN,
  confidence                  STRING,
  caveats                     STRING,
  assessment_json             STRING               -- the full Assessment, for fidelity
);
```

- `readings` uses the same column names and units `predict.py` already reads.
- `assessments` is append-only: one row per agent run. Repeated runs build a risk history.

## Dashboard

| Panel | Source | Shows |
|---|---|---|
| Wounds needing attention | latest assessment per wound | Count where the tier is `2 treat` or `3 intensive`, or clinician review is recommended |
| All wounds | latest assessment per wound | Risk, tier, confidence, review flag, agent summary, data-quality flags, next dose; highest risk first |
| Sensor trends | `readings` | pH, temperature and impedance over time, filtered by wound |
| Risk history | `assessments` | Risk score at each assessment, per wound |

"Latest assessment per wound" is the row with the newest `generated_at` for each wound.
The dashboard title states that the data is simulated.

## Safety of the SQL

- Every value that comes from outside the code (wound ids in filters, and all assessment
  fields including the agent's free text) is passed as a named statement parameter.
- The bulk reading insert uses literal values for speed, 500 rows per statement. It only ever writes numbers,
  timestamps formatted by pandas, a wound id that has passed validation, and a `source`
  from the fixed set above.
- Wound ids must match `^[A-Za-z0-9_.-]{1,64}$`. Catalog and schema names must match
  `^[A-Za-z0-9_]+$`. Anything else raises `ValueError` before any SQL is built.
- Missing sensor values are written as `NULL`.

## Failure handling

| Situation | Behaviour |
|---|---|
| A required setting is missing | Message naming the missing settings, exit code 1, matching the existing API-key check |
| Warehouse is starting | The store polls for up to two minutes, then raises a clear timeout error |
| A statement fails | `RuntimeError` carrying the Databricks error message |
| A wound has no readings | `ValueError` naming the wound, matching `FileDataSource` |
| Saving fails after an assessment | The assessment has already been printed; the error is reported and the exit code is non-zero |
| The agent refuses one wound during `--all` | Reported, the run continues, exit code 2 at the end |

## Testing

- **Unit tests** (`tests/test_databricks_store.py`), using a fake `execute`:
  - `get_history` turns string rows into a typed, sorted DataFrame that `run_offline`
    accepts and assesses.
  - `get_history` raises on a wound with no rows, and sets `is_dummy` from `source`.
  - `upload_readings` deletes before inserting, chunks large uploads, writes `NULL` for
    missing values, and rejects bad wound ids and unknown sources.
  - `assessment_row` flattens an assessment with and without agent notes.
  - `from_env` names every missing setting.
- **CLI test**: `main.py --databricks --offline` with a fake store saves one assessment;
  `--all` without `--databricks` is rejected.
- **Live round trip** (`tests/test_databricks_live.py`), skipped unless the Databricks
  settings are present: upload a short wound under a throwaway id, read it back, assess it
  offline, save the assessment, then delete the test rows from both tables.
- The existing tests must still pass unchanged.

## Demo run sheet

1. `python patch_gateway.py --demo-cohort`
2. `python main.py --databricks --all`
3. Open the dashboard: five wounds, ranked by risk, with the agent's summaries.
4. Live: `python patch_gateway.py --wound wound-006 --scenario infected --seed 2`, then
   `python main.py --databricks --wound wound-006 -v`, then refresh the dashboard.

## Assumptions to check before building

The first implementation step is a short connection check. If any of these fail, stop and
revisit the design.

1. The workspace allows a personal access token and the SQL Statement Execution API.
2. A serverless SQL warehouse exists and can be started.
3. The `workspace` catalog exists and allows creating a schema. If not, set
   `DATABRICKS_CATALOG`.
4. `databricks-sdk` installs alongside the pinned `pandas` and `numpy` on Python 3.12+.

## Needed from the team

- An access token and the SQL warehouse id from the workspace, placed in `.env`.
- About ten minutes to build the dashboard in the Databricks UI from the supplied queries.

## Not included

- Training, experiment tracking or model serving on Databricks.
- The Amethyst app reading from Databricks.
- Parsing the firmware's Bluetooth lines. The firmware reports capacitance, not impedance,
  and no glucose, so it cannot feed the model yet; that is an existing open item.
- Replaying readings in real time.
- Real patient data. Everything stored is simulated, and the workspace must not be used
  for real patient data.
