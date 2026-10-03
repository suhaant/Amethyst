# Databricks notebook source
# MAGIC %md
# MAGIC # 01 · Ingest — glucose data + simulated wounds → Delta (Bronze)
# MAGIC
# MAGIC Creates the schema and a `raw` volume, loads the real BIG IDEAs Dexcom glucose files,
# MAGIC runs the wound simulator, and writes Bronze Delta tables:
# MAGIC
# MAGIC | Table | Contents |
# MAGIC |---|---|
# MAGIC | `readings_bronze` | 600 simulated training wounds × 14 days, every 30 min (403,200 rows, with labels) |
# MAGIC | `demo_readings_bronze` | 20 held-out demo wounds from participants 14-16, **no labels** |
# MAGIC | `demo_answer_key` | labels for the demo wounds (grading only) |
# MAGIC | `glucose_participants` | the 16 real CGM participants |
# MAGIC
# MAGIC **Glucose data**: BIG IDEAs Lab Glycemic Variability and Wearable Device Data v1.1.3,
# MAGIC PhysioNet, ODC-By 1.0 — https://physionet.org/content/big-ideas-glycemic-wearable/1.1.3/
# MAGIC
# MAGIC Run this notebook from a **Git folder** clone of the repo (Workspace → Create → Git folder),
# MAGIC so the project's Python files are importable.

# COMMAND ----------

# MAGIC %pip install xgboost
# MAGIC %restart_python

# COMMAND ----------

dbutils.widgets.text("catalog", "workspace", "Catalog")
dbutils.widgets.text("schema", "wolfhacks", "Schema")
CATALOG = dbutils.widgets.get("catalog")
SCHEMA = dbutils.widgets.get("schema")
FQ = f"{CATALOG}.{SCHEMA}"

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {FQ}")
spark.sql(f"CREATE VOLUME IF NOT EXISTS {FQ}.raw")
VOL = f"/Volumes/{CATALOG}/{SCHEMA}/raw"
GLUCOSE_DIR = f"{VOL}/bigideas"
print("schema:", FQ, "| volume:", VOL)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Get the glucose files into the volume
# MAGIC Tries to download from PhysioNet (~3 MB). If outbound internet is blocked (e.g. Free Edition),
# MAGIC run `./download_glucose.sh` on your laptop and upload the `data/bigideas` folder to
# MAGIC **Catalog → your schema → raw volume → `bigideas/`**, then re-run.

# COMMAND ----------

import os
import urllib.request

def fetch_glucose(dst):
    base = "https://physionet.org/files/big-ideas-glycemic-wearable/1.1.3"
    os.makedirs(dst, exist_ok=True)
    for f in ["Demographics.csv", "LICENSE.txt"]:
        urllib.request.urlretrieve(f"{base}/{f}", f"{dst}/{f}")
    for i in range(1, 17):
        pid = f"{i:03d}"
        os.makedirs(f"{dst}/{pid}", exist_ok=True)
        for f in [f"Dexcom_{pid}.csv", f"Food_Log_{pid}.csv"]:
            urllib.request.urlretrieve(f"{base}/{pid}/{f}", f"{dst}/{pid}/{f}")

if not os.path.exists(f"{GLUCOSE_DIR}/Demographics.csv"):
    try:
        fetch_glucose(GLUCOSE_DIR)
        print("downloaded glucose data to", GLUCOSE_DIR)
    except Exception as e:
        raise RuntimeError(
            f"Could not download from PhysioNet ({e}). Upload data/bigideas to {GLUCOSE_DIR} and re-run."
        )
else:
    print("glucose data already in", GLUCOSE_DIR)

# COMMAND ----------

import sys

REPO = os.path.dirname(os.getcwd())          # notebook lives in <repo>/databricks
sys.path.insert(0, REPO)
os.environ["WOUND_GLUCOSE_DIR"] = GLUCOSE_DIR  # must be set before importing glucose_data

import numpy as np
import pandas as pd
import generate_data as G
from glucose_data import load_participants

STEP_MIN, DAYS = 30, 14
people = load_participants(STEP_MIN)
print(len(people), "participants loaded")

part = pd.DataFrame([{"participant_id": pid, "hba1c": p["hba1c"], "complete_days": len(p["days"]),
                      "mean_glucose_mgdl": float(np.concatenate(p["days"]).mean())}
                     for pid, p in people.items()])
spark.createDataFrame(part).write.mode("overwrite").option("overwriteSchema", "true") \
    .saveAsTable(f"{FQ}.glucose_participants")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Simulate training wounds → `readings_bronze`

# COMMAND ----------

def simulate(n_wounds, days, seed, pids, prefix):
    rng = np.random.default_rng(seed)
    hours = np.arange(0, days * 24, STEP_MIN / 60)
    assign = rng.permutation(np.resize(sorted(pids), n_wounds))
    df = pd.concat([G.simulate_wound(w, hours, rng, int(assign[w]), people[int(assign[w])])
                    for w in range(n_wounds)], ignore_index=True)
    df["wound_id"] = prefix + df["wound_id"].astype(str).str.zfill(3)
    start = pd.Timestamp("2026-10-01 08:00")
    df["timestamp"] = start + pd.to_timedelta(df["hour"], unit="h")
    df["artifact"] = df["artifact"].astype(int)
    return df

train = simulate(600, DAYS, seed=42, pids=list(people), prefix="W")
spark.createDataFrame(train).write.mode("overwrite").option("overwriteSchema", "true") \
    .saveAsTable(f"{FQ}.readings_bronze")
display(spark.sql(f"SELECT outcome, count(DISTINCT wound_id) wounds, count(*) readings "
                  f"FROM {FQ}.readings_bronze GROUP BY outcome"))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Held-out demo wounds → `demo_readings_bronze` + `demo_answer_key`
# MAGIC Participants 14-16, new seed. `02_train_mlflow` trains its *demo-check* model without them.

# COMMAND ----------

HOLDOUT = [14, 15, 16]
demo = simulate(20, 10, seed=2026, pids=HOLDOUT, prefix="DEMO-")
demo["patient_id"] = "P" + demo["participant_id"].astype(str)
inputs = ["wound_id", "patient_id", "timestamp", "ph", "temp_c", "impedance_kohm",
          "blood_glucose_mgdl", "wound_glucose_mM"]
spark.createDataFrame(demo[inputs]).write.mode("overwrite").option("overwriteSchema", "true") \
    .saveAsTable(f"{FQ}.demo_readings_bronze")
spark.createDataFrame(demo[["wound_id", "timestamp", "hour", "label", "artifact", "outcome",
                            "infection_onset_h"]]) \
    .write.mode("overwrite").option("overwriteSchema", "true").saveAsTable(f"{FQ}.demo_answer_key")
print("demo wounds:", demo.wound_id.nunique(), "| readings:", len(demo))
